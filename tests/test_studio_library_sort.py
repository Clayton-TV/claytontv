"""Studio Library column sorting (sortable datatable).

Server-side sort (the list is paginated, so sorting must happen in the DB before
the page slice). Covers the plain columns, the coalesced date, the two M2M
columns (speaker via Min, series via subquery), direction toggling, NULL
placement, invalid-input fallback, and that sort survives the status filter.
"""

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.models.video import DRAFT, PUBLISHED
from tests.factories import SeriesFactory, SpeakerFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

User = get_user_model()
PASSWORD = "pw-correct-horse-1"  # gitleaks:allow


def _names(result):
    return [r["name"] for r in result["videos"]]


def _login_editor(client):
    user = User.objects.create_user(username="editor", password=PASSWORD)
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    client.login(username="editor", password=PASSWORD)


# --- plain columns -------------------------------------------------------- #


def test_sort_by_title_ascending_and_descending():
    VideoFactory(name="Banana")
    VideoFactory(name="Apple")
    VideoFactory(name="Cherry")

    assert _names(services.list_videos(sort="title", direction="asc")) == ["Apple", "Banana", "Cherry"]
    assert _names(services.list_videos(sort="title", direction="desc")) == ["Cherry", "Banana", "Apple"]


def test_sort_by_runtime_puts_nulls_last_both_directions():
    VideoFactory(name="Short", duration_seconds=60)
    VideoFactory(name="Long", duration_seconds=3600)
    VideoFactory(name="Unknown", duration_seconds=None)

    asc = _names(services.list_videos(sort="runtime", direction="asc"))
    assert asc == ["Short", "Long", "Unknown"]  # null last even ascending
    desc = _names(services.list_videos(sort="runtime", direction="desc"))
    assert desc == ["Long", "Short", "Unknown"]  # null still last


def test_sort_by_status():
    VideoFactory(name="Pub", status=PUBLISHED)
    VideoFactory(name="Draft", status=DRAFT)
    # draft < published alphabetically
    assert _names(services.list_videos(sort="status", direction="asc")) == ["Draft", "Pub"]


def test_sort_by_date_uses_recorded_then_created_coalesce():
    # "Newer" has no recorded date → falls back to its (later) created date, which
    # must still sort it after "Older" whose recorded date is earlier.
    VideoFactory(name="Older", date_recorded=datetime.date(2020, 1, 1), date_created=datetime.date(2026, 1, 1))
    VideoFactory(name="Newer", date_recorded=None, date_created=datetime.date(2024, 1, 1))

    assert _names(services.list_videos(sort="date", direction="asc")) == ["Older", "Newer"]


# --- M2M columns ---------------------------------------------------------- #


def test_sort_by_speaker_via_m2m():
    v1 = VideoFactory(name="Zebra talk")
    v1.speaker.add(SpeakerFactory(name="Adams, Anne"))
    v2 = VideoFactory(name="Apple talk")
    v2.speaker.add(SpeakerFactory(name="Zimmer, Zoe"))

    # Sorted by SPEAKER, not title.
    assert _names(services.list_videos(sort="speaker", direction="asc")) == ["Zebra talk", "Apple talk"]


def test_sort_by_series_via_m2m_subquery():
    v1 = VideoFactory(name="In Genesis")
    SeriesFactory(name="Aardvark Studies").videos.add(v1)
    v2 = VideoFactory(name="In Exodus")
    SeriesFactory(name="Zoology Studies").videos.add(v2)

    assert _names(services.list_videos(sort="series", direction="asc")) == ["In Genesis", "In Exodus"]


# --- robustness ----------------------------------------------------------- #


def test_invalid_sort_falls_back_to_newest_first():
    older = VideoFactory(name="Older", date_created=datetime.date(2026, 1, 1))
    newer = VideoFactory(name="Newer", date_created=datetime.date(2026, 6, 1))

    result = services.list_videos(sort="bogus_column", direction="sideways")
    # Default order is newest-created first, and the bad direction is ignored.
    assert _names(result) == ["Newer", "Older"]
    assert older.name and newer.name  # (sanity)


def test_sort_respects_status_filter():
    VideoFactory(name="Apple", status=DRAFT)
    VideoFactory(name="Banana", status=PUBLISHED)
    VideoFactory(name="Cherry", status=DRAFT)

    result = services.list_videos(status=DRAFT, sort="title", direction="asc")
    assert _names(result) == ["Apple", "Cherry"]  # Banana (published) excluded


# --- view wiring ---------------------------------------------------------- #


def test_library_view_echoes_sort_and_dir(client):
    _login_editor(client)
    VideoFactory(name="A")
    props = inertia_page(client.get("/studio/", {"sort": "title", "dir": "asc"}))["props"]
    assert props["sort"] == "title"
    assert props["dir"] == "asc"


def test_library_view_defaults_sort_empty(client):
    _login_editor(client)
    VideoFactory(name="A")
    props = inertia_page(client.get("/studio/"))["props"]
    assert props["sort"] == ""
    assert props["dir"] == "desc"
