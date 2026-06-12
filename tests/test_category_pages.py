import pytest

from tests.factories import SeriesFactory, TopicFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def make_series(name, video_count, **kwargs):
    series = SeriesFactory(name=name, **kwargs)
    for _ in range(video_count):
        series.videos.add(VideoFactory())
    return series


class TestSeriesIndex:
    def test_lists_series_with_m2m_counts_most_popular_first(self, client):
        make_series("Small", 1)
        make_series("Big", 3)
        SeriesFactory(name="Empty husk")  # never linked → hidden

        page = inertia_page(client.get("/series/"))

        assert page["component"] == "SeriesIndex"
        entries = page["props"]["series"]
        assert [(s["name"], s["videosCount"]) for s in entries] == [("Big", 3), ("Small", 1)]
        assert page["props"]["total"] == 2

    def test_filters_by_query(self, client):
        make_series("Romans for Everyone", 1)
        make_series("Acts in a Month", 1)

        props = inertia_page(client.get("/series/", {"q": "romans"}))["props"]

        assert [s["name"] for s in props["series"]] == ["Romans for Everyone"]
        assert props["query"] == "romans"

    def test_paginates(self, client):
        for n in range(30):
            make_series(f"Series {n:02d}", 1)

        props = inertia_page(client.get("/series/", {"page": 2}))["props"]

        assert len(props["series"]) == 6  # 30 total, 24 per page
        assert props["has_prev_page"] is True
        assert props["has_next_page"] is False


class TestTopicsIndex:
    def test_groups_topics_by_legacy_category(self, client):
        theology = TopicFactory(name="The Grace of God", category="THEOLOGY - GOD")
        life = TopicFactory(name="Prayer", category="CHRISTIAN LIFE")
        video = VideoFactory()
        video.topic.add(theology, life)

        page = inertia_page(client.get("/topic/"))

        assert page["component"] == "TopicsIndex"
        groups = {g["category"]: [t["name"] for t in g["topics"]] for g in page["props"]["topic_groups"]}
        assert groups == {"THEOLOGY - GOD": ["The Grace of God"], "CHRISTIAN LIFE": ["Prayer"]}
        assert page["props"]["total"] == 2


class TestSeriesDetail:
    def test_shows_episodes_from_the_series_videos_m2m(self, client):
        """The old page paginated series.video_set (the never-populated FK), so
        every series detail page showed zero episodes."""
        make_series("John's Gospel", 2, summary="A walk through John.")

        page = inertia_page(client.get("/series/John%27s%20Gospel"))

        assert page["component"] == "SeriesDetail"
        props = page["props"]
        assert props["series_meta"]["name"] == "John's Gospel"
        assert props["series_meta"]["summary"] == "A walk through John."
        assert props["series_meta"]["videosCount"] == 2
        assert len(props["episodes"]) == 2  # v2: numbered episode rows (see test_destination_pages)

    def test_unknown_series_renders_not_found(self, client):
        response = client.get("/series/Nope")
        assert inertia_page(response)["props"]["title"].startswith("Series not found")


def test_search_counts_series_videos_via_m2m(client):
    make_series("Amazing Grace", 2)

    page = inertia_page(client.get("/search", {"search": "amazing"}))

    entry = next(c for c in page["props"]["categories"] if c["name"] == "Amazing Grace")
    assert entry["videosCount"] == 2


def test_watch_page_series_chip_uses_m2m_membership(client):
    series = make_series("Acts", 1)
    video = series.videos.first()

    page = inertia_page(client.get(f"/video/{video.id}"))

    assert page["props"]["video_metadata"]["series"]["name"] == "Acts"
