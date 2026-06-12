import pytest

from tests.factories import SeriesFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_homepage_renders_curated_welcome_props(client):
    series = SeriesFactory(name="Romans for Everyone", summary="A walk through Romans.")
    topic = TopicFactory(name="Grace")
    video = VideoFactory(name="Romans 8 - More Than Conquerors")
    video.topic.add(topic)
    series.videos.add(video)

    response = client.get("/")

    assert response.status_code == 200
    page = inertia_page(response)
    assert page["component"] == "Welcome"

    props = page["props"]
    assert [v["name"] for v in props["latest_videos"]] == ["Romans 8 - More Than Conquerors"]
    # "Watch Live" is for genuinely live/upcoming broadcasts (YouTube API,
    # Epic 4) — past stream recordings must never appear there as if live.
    assert props["livestreams"] == []

    (topic_entry,) = props["topics_data"]
    assert topic_entry["name"] == "Grace"
    assert topic_entry["videosCount"] == 1

    (series_entry,) = props["featured_series"]
    assert series_entry["name"] == "Romans for Everyone"
    assert series_entry["summary"] == "A walk through Romans."
    assert series_entry["videosCount"] == 1

    assert props["topics_total"] == 1


def test_homepage_counts_videos_linked_via_the_importer_relations(client):
    """Counts must use the relations the IMPORTER writes, which differ per model:
    topics link via Video.topic (link_videos), series via the Series.videos M2M
    (link_series). Counting the wrong relation made every series show 0."""
    topic = TopicFactory()
    series = SeriesFactory()
    for _ in range(3):
        video = VideoFactory()  # deliberately NOT VideoFactory(series=...) — the FK is never set in real data
        video.topic.add(topic)
        series.videos.add(video)

    page = inertia_page(client.get("/"))

    assert page["props"]["topics_data"][0]["videosCount"] == 3
    assert page["props"]["featured_series"][0]["videosCount"] == 3


def test_homepage_is_curated_not_exhaustive(client):
    """The previous homepage shipped every series (1,069 cards, ~300 kB of
    props). The redesign sends a curated slice; browsing lives one click deeper."""
    for series in SeriesFactory.create_batch(10):
        series.videos.add(VideoFactory())
    for topic in TopicFactory.create_batch(20):
        video = VideoFactory()
        video.topic.add(topic)
    SeriesFactory(name="Empty husk")  # no videos → never featured

    props = inertia_page(client.get("/"))["props"]

    assert len(props["featured_series"]) == 4
    assert len(props["topics_data"]) == 12
    assert len(props["latest_videos"]) == 6
    assert "Empty husk" not in [s["name"] for s in props["featured_series"]]
    assert props["topics_total"] == 20


def test_homepage_query_count_does_not_grow_with_catalogue_size(client, django_assert_max_num_queries):
    """Regression test for the production 504s of 2026-06-12: the homepage ran
    two queries per series and one per topic (~2,250 queries against the full
    catalogue), wedging every gunicorn worker. Query count must stay flat no
    matter how many topics/series exist."""
    TopicFactory.create_batch(20)
    for series in SeriesFactory.create_batch(20):
        series.videos.add(VideoFactory())

    with django_assert_max_num_queries(8):
        response = client.get("/")

    assert response.status_code == 200
