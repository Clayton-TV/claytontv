"""Studio Library (Epic 3, Slice 2): the editor content list + its mutations.

What makes the Library special vs every public surface: it shows ALL statuses
(drafts included). The mutations (publish/unpublish/delete, single + bulk) are
editor-gated and CSRF-protected, and a publish flip round-trips to the public
site (proven via /api/palette).
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from app.auth import EDITORS_GROUP
from catalogue.models.video import DRAFT, PUBLISHED, Video
from tests.factories import SeriesFactory, SpeakerFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

User = get_user_model()
PASSWORD = "pw-correct-horse-1"  # gitleaks:allow


def make_editor(username="editor"):
    user = User.objects.create_user(username=username, password=PASSWORD)
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    return user


def login_editor(client, username="editor"):
    make_editor(username)
    client.login(username=username, password=PASSWORD)


def library_props(client, **params):
    return inertia_page(client.get("/studio/", params))["props"]


# --- gating ---------------------------------------------------------------


def test_non_editor_forbidden_on_library(client):
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    assert client.get("/studio/").status_code == 403


def test_anonymous_redirected_from_library(client):
    response = client.get("/studio/")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/studio/login")


@pytest.mark.parametrize(
    "path",
    ["/studio/videos/1/status", "/studio/videos/bulk-status", "/studio/videos/delete"],
)
def test_non_editor_forbidden_on_mutations(client, path):
    VideoFactory(id="1")
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    response = client.post(path, {"status": PUBLISHED, "ids": ["1"]})
    assert response.status_code == 403


@pytest.mark.parametrize(
    "path",
    ["/studio/videos/1/status", "/studio/videos/bulk-status", "/studio/videos/delete"],
)
def test_anonymous_redirected_from_mutations(client, path):
    VideoFactory(id="1")
    response = client.post(path, {"status": PUBLISHED, "ids": ["1"]})
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/studio/login")


def test_mutations_require_post(client):
    login_editor(client)
    assert client.get("/studio/videos/bulk-status").status_code == 405
    assert client.get("/studio/videos/delete").status_code == 405


def test_mutations_are_csrf_protected(db):
    # A CSRF-enforcing client (the default app pipeline runs CsrfViewMiddleware);
    # a POST without a valid token is rejected before the view runs.
    from django.test import Client

    csrf_client = Client(enforce_csrf_checks=True)
    make_editor("ed_csrf")
    csrf_client.login(username="ed_csrf", password=PASSWORD)
    video = VideoFactory(status=DRAFT)
    response = csrf_client.post(f"/studio/videos/{video.id}/status", {"status": PUBLISHED})
    assert response.status_code == 403
    video.refresh_from_db()
    assert video.status == DRAFT


# --- the list shows all statuses -----------------------------------------


def test_library_lists_both_draft_and_published(client):
    login_editor(client)
    VideoFactory(name="Live Talk", status=PUBLISHED)
    VideoFactory(name="Hidden Draft", status=DRAFT)

    names = {v["name"] for v in library_props(client)["videos"]}
    assert names == {"Live Talk", "Hidden Draft"}


def test_library_row_carries_speakers_and_series(client):
    login_editor(client)
    video = VideoFactory(name="Sermon", status=PUBLISHED)
    video.speaker.add(SpeakerFactory(name="Jane Preacher"))
    # Series membership lives on the Series.videos M2M (CLAUDE.md), not the FK.
    series = SeriesFactory(name="Romans Study")
    series.videos.add(video)

    row = next(v for v in library_props(client)["videos"] if v["name"] == "Sermon")
    assert row["speakers"] == ["Jane Preacher"]
    assert row["series"] == "Romans Study"
    assert row["status"] == PUBLISHED


def test_status_filter_narrows(client):
    login_editor(client)
    VideoFactory(name="Live One", status=PUBLISHED)
    VideoFactory(name="Draft One", status=DRAFT)

    draft_names = {v["name"] for v in library_props(client, status=DRAFT)["videos"]}
    assert draft_names == {"Draft One"}

    published_names = {v["name"] for v in library_props(client, status=PUBLISHED)["videos"]}
    assert published_names == {"Live One"}


def test_search_narrows(client):
    login_editor(client)
    VideoFactory(name="Grace Abounds", status=DRAFT)
    VideoFactory(name="Something Else", status=PUBLISHED)

    names = {v["name"] for v in library_props(client, q="grace")["videos"]}
    assert names == {"Grace Abounds"}


# --- mutations ------------------------------------------------------------


def test_set_status_publishes_then_unpublishes_with_public_round_trip(client):
    login_editor(client)
    video = VideoFactory(name="Roundtrip Talk", status=DRAFT)

    # Publish → appears on a public surface (the palette).
    response = client.post(f"/studio/videos/{video.id}/status", {"status": PUBLISHED})
    assert response.status_code == 302
    video.refresh_from_db()
    assert video.status == PUBLISHED
    palette = client.get("/api/palette", {"q": "roundtrip"}).json()
    assert any(v["name"] == "Roundtrip Talk" for v in palette["videos"])

    # Unpublish → drops from the public surface, but still in the Library.
    client.post(f"/studio/videos/{video.id}/status", {"status": DRAFT})
    video.refresh_from_db()
    assert video.status == DRAFT
    palette = client.get("/api/palette", {"q": "roundtrip"}).json()
    assert not any(v["name"] == "Roundtrip Talk" for v in palette["videos"])
    library_names = {v["name"] for v in library_props(client)["videos"]}
    assert "Roundtrip Talk" in library_names


def test_set_status_rejects_unknown_status(client):
    login_editor(client)
    video = VideoFactory(status=PUBLISHED)
    client.post(f"/studio/videos/{video.id}/status", {"status": "archived"})
    video.refresh_from_db()
    assert video.status == PUBLISHED


def test_bulk_status_changes_many(client):
    login_editor(client)
    a = VideoFactory(status=DRAFT)
    b = VideoFactory(status=DRAFT)
    c = VideoFactory(status=DRAFT)

    response = client.post(
        "/studio/videos/bulk-status",
        {"status": PUBLISHED, "ids": [a.id, b.id]},
    )
    assert response.status_code == 302
    assert Video.objects.filter(status=PUBLISHED).count() == 2
    c.refresh_from_db()
    assert c.status == DRAFT


def test_delete_removes_videos(client):
    login_editor(client)
    a = VideoFactory()
    b = VideoFactory()
    keep = VideoFactory()

    response = client.post("/studio/videos/delete", {"ids": [a.id, b.id]})
    assert response.status_code == 302
    assert not Video.objects.filter(id__in=[a.id, b.id]).exists()
    assert Video.objects.filter(id=keep.id).exists()


def test_mutation_preserves_filters_via_next(client):
    login_editor(client)
    video = VideoFactory(status=DRAFT)
    response = client.post(
        f"/studio/videos/{video.id}/status",
        {"status": PUBLISHED, "next": "/studio/?status=draft&q=foo"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio/?status=draft&q=foo"


def test_mutation_rejects_offsite_next(client):
    login_editor(client)
    video = VideoFactory(status=DRAFT)
    response = client.post(
        f"/studio/videos/{video.id}/status",
        {"status": PUBLISHED, "next": "https://evil.example/"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio"
