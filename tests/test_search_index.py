"""Typesense index building (catalogue/search.py).

These tests are pure-Python doc-shape + count checks and a guarded live
round-trip. The doc/count tests need no Typesense; the live test skips unless a
reachable Typesense is configured (TYPESENSE_API_KEY set + container up), so CI
without a container stays green.
"""

import datetime

import pytest

from catalogue import search
from tests.factories import (
    BibleBookFactory,
    SeriesFactory,
    SpeakerFactory,
    TopicFactory,
    VideoFactory,
)
from tests.utils import typesense_env_config

pytestmark = pytest.mark.django_db


def test_get_client_is_none_without_api_key(settings):
    settings.TYPESENSE = {**settings.TYPESENSE, "api_key": ""}
    assert search.get_client() is None


def test_search_raises_unavailable_on_connection_failure(settings):
    # Configured but unreachable (dead port). The client raises a raw httpx
    # transport error; the helper must convert it to SearchUnavailableError so
    # the view treats an outage as a quiet ORM fallback, not a Sentry-worthy bug.
    settings.TYPESENSE = {
        "api_key": "x",
        "host": "127.0.0.1",
        "port": "9",  # discard port — connection refused immediately
        "protocol": "http",
        "connection_timeout_seconds": 1,
    }
    with pytest.raises(search.SearchUnavailableError):
        search.search_videos("anything")


def test_build_video_doc_shape():
    video = VideoFactory(
        name="Romans 8",
        description="The Spirit and adoption.",
        is_livestream=True,
        date_recorded=datetime.date(2026, 3, 4),
    )

    doc = search.build_video_doc(video)

    assert doc["id"] == f"video:{video.pk}"
    assert doc["kind"] == search.KIND_VIDEO
    assert doc["name"] == "Romans 8"
    assert doc["text"] == "The Spirit and adoption."
    assert doc["url"] == f"/video/{video.pk}"
    assert doc["videos_count"] == 0
    assert doc["is_livestream"] is True
    assert doc["date_display"] == "2026-03-04"
    assert isinstance(doc["date_epoch"], int)


def test_video_doc_falls_back_to_date_created_when_unrecorded():
    video = VideoFactory(date_recorded=None, date_created=datetime.date(2026, 2, 1))

    doc = search.build_video_doc(video)

    assert doc["date_display"] == "2026-02-01"


def test_build_category_doc_shape():
    doc = search.build_category_doc(
        kind=search.KIND_SERIES, pk="S007", name="Romans", text="A study.", url="/series/S007", videos_count=12
    )

    assert doc == {
        "id": "series:S007",
        "kind": "series",
        "pk": "S007",
        "name": "Romans",
        "text": "A study.",
        "url": "/series/S007",
        "videos_count": 12,
    }


def test_iter_content_docs_counts_series_via_m2m_not_the_decoy_fk():
    # The decoy: Video.series FK is never populated. A series' real video count
    # lives on the Series.videos M2M — the same relation the views Count.
    series = SeriesFactory(name="Romans for Everyone")
    series.videos.add(VideoFactory(), VideoFactory())
    VideoFactory(series=series)  # FK-linked only: must NOT inflate the count

    docs = {d["id"]: d for d in search.iter_content_docs()}

    assert docs[f"series:{series.pk}"]["videos_count"] == 2
    assert docs[f"series:{series.pk}"]["kind"] == "series"


def test_iter_content_docs_covers_each_kind_with_counts():
    speaker = SpeakerFactory(name="Paul")
    speaker.video_set.add(VideoFactory())
    topic = TopicFactory(name="Grace")
    VideoFactory().topic.add(topic)
    book = BibleBookFactory()  # GEN / "Genesis"
    VideoFactory().bible_book.add(book)

    docs = {d["id"]: d for d in search.iter_content_docs()}

    assert docs[f"speaker:{speaker.pk}"]["videos_count"] == 1
    assert docs[f"topic:{topic.pk}"]["videos_count"] == 1
    # Bible books index the display name, not the choice code.
    assert docs[f"book:{book.pk}"]["name"] == "Genesis"
    assert docs[f"book:{book.pk}"]["videos_count"] == 1


# --------------------------------------------------------------------------- #
# Guarded live round-trip — skipped unless a reachable Typesense is configured.
# --------------------------------------------------------------------------- #


@pytest.fixture
def live_client(settings):
    # test_settings disables Typesense; opt back in from the environment for this
    # test only so the rest of the suite stays deterministic on the ORM path.
    config = typesense_env_config()
    if config is None:
        pytest.skip("Typesense not configured (set TYPESENSE_API_KEY)")
    settings.TYPESENSE = config
    client = search.get_client()
    try:
        client.collections.retrieve()
    except Exception:
        pytest.skip("Typesense not reachable")
    return client


def test_reindex_then_typo_and_synonym_search(live_client):
    VideoFactory(name="The Sermon on the Mount", description="Matthew 5-7")
    VideoFactory(name="Unrelated clip")

    indexed = search.reindex()
    assert indexed >= 2

    # Typo tolerance: "sermom" → "sermon".
    hits, found = search.search_videos("sermom", per_page=10)
    assert any("Sermon on the Mount" in h.name for h in hits)
    assert found >= 1

    # Synonym: "talk" is configured as a synonym of "sermon".
    hits, _ = search.search_videos("talk on the mount", per_page=10)
    assert any("Sermon on the Mount" in h.name for h in hits)


def test_reindex_then_category_search_groups_by_kind_with_counts(live_client):
    series = SeriesFactory(name="Galatians Unpacked")
    series.videos.add(VideoFactory(), VideoFactory())

    search.reindex()

    hits = search.search_categories("galatins", kinds=[search.KIND_SERIES, search.KIND_SPEAKER])
    match = next(h for h in hits if h.name == "Galatians Unpacked")
    assert match.kind == "series"
    assert match.videos_count == 2  # baked in — no per-hit ORM query
    assert match.url
