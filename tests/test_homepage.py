import pytest

from tests.factories import SeriesFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_homepage_renders_welcome_with_catalogue_props(client):
    series = SeriesFactory(name="Romans for Everyone")
    topic = TopicFactory(name="Grace")
    video = VideoFactory(name="Romans 8 - More Than Conquerors", series=series)
    video.topic.add(topic)
    VideoFactory(name="Sunday Live", is_livestream=True)

    response = client.get("/")

    assert response.status_code == 200
    page = inertia_page(response)
    assert page["component"] == "Welcome"

    props = page["props"]
    assert [v["name"] for v in props["latest_videos"]] == ["Romans 8 - More Than Conquerors"]
    assert [v["name"] for v in props["livestreams"]] == ["Sunday Live"]

    (topic_entry,) = props["topics_data"]
    assert topic_entry["name"] == "Grace"
    assert topic_entry["videosCount"] == 1

    (series_entry,) = props["series_data"]
    assert series_entry["name"] == "Romans for Everyone"
    assert series_entry["videosCount"] == 1


def test_homepage_counts_videos_linked_via_the_video_side(client):
    """Topic/Series have their own (unused) videos M2M; the homepage must count
    the relations the rest of the app writes: Video.topic and Video.series."""
    topic = TopicFactory()
    series = SeriesFactory()
    for _ in range(3):
        video = VideoFactory(series=series)
        video.topic.add(topic)

    page = inertia_page(client.get("/"))

    assert page["props"]["topics_data"][0]["videosCount"] == 3
    assert page["props"]["series_data"][0]["videosCount"] == 3


def test_homepage_query_count_does_not_grow_with_catalogue_size(client, django_assert_max_num_queries):
    """Regression test for the production 504s of 2026-06-12: the homepage ran
    two queries per series and one per topic (~2,250 queries against the full
    catalogue), wedging every gunicorn worker. Query count must stay flat no
    matter how many topics/series exist."""
    TopicFactory.create_batch(20)
    for series in SeriesFactory.create_batch(20):
        VideoFactory(series=series)

    with django_assert_max_num_queries(8):
        response = client.get("/")

    assert response.status_code == 200
