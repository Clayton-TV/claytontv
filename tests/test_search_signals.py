"""Live indexing via post_save/post_delete signals (catalogue/search_signals.py).

The inert-when-unavailable test runs with no Typesense (the default in
test_settings) and is the important guarantee: a model save must never be broken
by a search outage. The live tests prove the signal actually upserts/deletes.
"""

import pytest

from catalogue import search
from tests.factories import SeriesFactory, VideoFactory
from tests.utils import typesense_env_config

pytestmark = pytest.mark.django_db


def test_saving_a_video_never_raises_when_typesense_unavailable():
    # test_settings disables Typesense; the signal must no-op, not raise.
    video = VideoFactory(name="Nahum Note")
    assert video.pk  # the save itself succeeded


def test_deleting_a_video_never_raises_when_typesense_unavailable():
    video = VideoFactory(name="Obadiah One")
    video.delete()  # signal fires; must be inert, not raise
    assert not type(video).objects.filter(pk=video.pk).exists()


# --------------------------------------------------------------------------- #
# Guarded live tests — prove the signal actually keeps the index in sync.
# --------------------------------------------------------------------------- #


@pytest.fixture
def live_index(settings):
    config = typesense_env_config()
    if config is None:
        pytest.skip("Typesense not configured (set TYPESENSE_API_KEY)")
    settings.TYPESENSE = config
    client = search.get_client()
    try:
        client.collections.retrieve()
    except Exception:
        pytest.skip("Typesense not reachable")
    search.recreate_collection(client)  # start from a clean, empty collection
    return client


def test_post_save_upserts_the_video_doc(live_index):
    VideoFactory(name="Habakkuk Hope")  # no reindex() — the signal indexes it

    hits, found = search.search_videos("habakkuk", per_page=5)

    assert found >= 1
    assert any("Habakkuk Hope" in h.name for h in hits)


def test_post_delete_removes_the_video_doc(live_index):
    video = VideoFactory(name="Zephaniah Zeal")
    video.delete()

    hits, _ = search.search_videos("zephaniah", per_page=5)

    assert not any("Zephaniah" in h.name for h in hits)


def test_post_save_indexes_a_category_with_its_count(live_index):
    series = SeriesFactory(name="Haggai Harvest")
    series.videos.add(VideoFactory(), VideoFactory())
    series.save()  # re-fire the signal so the doc carries the fresh count

    hits = search.search_categories("haggai", kinds=[search.KIND_SERIES])

    match = next(h for h in hits if h.name == "Haggai Harvest")
    assert match.videos_count == 2
