import json

import pytest

from tests.factories import SeriesFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

BELOW_FOLD = "featured_series,topics_data,topics_total"


def test_undated_videos_never_top_the_latest_rail(client):
    """The legacy admin holds programmes with an empty date (9 found in the
    2026-06 backfill). Postgres sorts DESC NULLS FIRST by default — without
    an explicit nulls_last they'd headline the homepage. SQLite can't fail
    this test (it sorts nulls last natively); it pins the intent."""
    VideoFactory(name="Undated upload", date_recorded=None)
    VideoFactory(name="Dated sermon", date_recorded="2026-06-07")

    rail = inertia_page(client.get("/"))["props"]["latest_videos"]

    assert rail[0]["name"] == "Dated sermon"


def below_fold_props(client):
    """Fetch the scroll-deferred sections the way WhenVisible does."""
    response = client.get(
        "/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="Welcome",
        HTTP_X_INERTIA_PARTIAL_DATA=BELOW_FOLD,
    )
    return json.loads(response.content)["props"]


def test_homepage_first_paint_is_hero_and_latest_only(client):
    """Below-the-fold sections are optional props loaded on scroll
    (WhenVisible); their queries must not run on first load."""
    video = VideoFactory(name="Romans 8 - More Than Conquerors")
    series = SeriesFactory(name="Romans for Everyone")
    series.videos.add(video)

    page = inertia_page(client.get("/"))

    assert page["component"] == "Welcome"
    props = page["props"]
    assert [v["name"] for v in props["latest_videos"]] == ["Romans 8 - More Than Conquerors"]
    assert props["livestreams"] == []
    assert "featured_series" not in props
    assert "topics_data" not in props


def test_below_fold_sections_load_on_demand(client):
    series = SeriesFactory(name="Romans for Everyone", summary="A walk through Romans.")
    topic = TopicFactory(name="Grace")
    video = VideoFactory()
    video.topic.add(topic)
    series.videos.add(video)

    props = below_fold_props(client)

    (series_entry,) = props["featured_series"]
    assert series_entry["name"] == "Romans for Everyone"
    assert series_entry["videosCount"] == 1
    (topic_entry,) = props["topics_data"]
    assert topic_entry["name"] == "Grace"
    assert topic_entry["videosCount"] == 1
    assert props["topics_total"] == 1


def test_below_fold_counts_use_importer_relations(client):
    """Topics link via Video.topic, series via the Series.videos M2M — counting
    the wrong relation silently returns 0."""
    topic = TopicFactory()
    series = SeriesFactory()
    for _ in range(3):
        video = VideoFactory()
        video.topic.add(topic)
        series.videos.add(video)

    props = below_fold_props(client)

    assert props["topics_data"][0]["videosCount"] == 3
    assert props["featured_series"][0]["videosCount"] == 3


def test_below_fold_is_curated_not_exhaustive(client):
    for series in SeriesFactory.create_batch(10):
        series.videos.add(VideoFactory())
    for topic in TopicFactory.create_batch(20):
        video = VideoFactory()
        video.topic.add(topic)
    SeriesFactory(name="Empty husk")

    props = below_fold_props(client)

    assert len(props["featured_series"]) == 4
    assert len(props["topics_data"]) == 12
    assert "Empty husk" not in [s["name"] for s in props["featured_series"]]
    assert props["topics_total"] == 20


def test_homepage_query_count_does_not_grow_with_catalogue_size(client, django_assert_max_num_queries):
    """Regression test for the production 504s of 2026-06-12. With below-fold
    sections deferred, first paint is leaner still."""
    TopicFactory.create_batch(20)
    for series in SeriesFactory.create_batch(20):
        series.videos.add(VideoFactory())

    # 6 for the page + 1 constant global "live now" nav flag (cheap exists()
    # on the small LiveStream table, shared by the Inertia middleware).
    with django_assert_max_num_queries(7):
        response = client.get("/")

    assert response.status_code == 200
