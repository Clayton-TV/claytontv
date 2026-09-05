"""The Latest page is a feed with a spine, not a wall of cards: videos are
grouped into editorial time buckets ("This week", "Last week", "Earlier in
June", "October 2024"), and a series that floods a bucket collapses into a
single series row. Spec: docs/DESIGN_SPEC.md § Latest."""

import datetime

import pytest

from app.feed import latest_feed
from tests.factories import SeriesFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

TODAY = datetime.date(2026, 6, 12)  # a Friday; week starts Monday 8th


def feed(page=1, today=TODAY):
    return latest_feed(page_num=page, today=today)


def test_groups_carry_editorial_time_labels_in_recency_order():
    today = datetime.date(2026, 6, 26)  # a Friday; week starts Monday 22nd
    VideoFactory(date_recorded=datetime.date(2026, 6, 24))  # this week (Wed)
    VideoFactory(date_recorded=datetime.date(2026, 6, 18))  # last week (Thu)
    VideoFactory(date_recorded=datetime.date(2026, 6, 5))  # earlier this month
    VideoFactory(date_recorded=datetime.date(2026, 4, 19))  # an older month

    labels = [g["label"] for g in feed(today=today)["groups"]]

    assert labels == ["This week", "Last week", "Earlier in June", "April 2026"]


def test_a_series_flooding_a_bucket_collapses_to_one_series_row():
    series = SeriesFactory(name="Romans")
    flood = [VideoFactory(date_recorded=datetime.date(2026, 6, 9 + n % 2)) for n in range(4)]
    series.videos.add(*flood)
    solo = VideoFactory(name="Standalone talk", date_recorded=datetime.date(2026, 6, 11))

    items = feed()["groups"][0]["items"]

    kinds = [(i["type"], i.get("name")) for i in items]
    assert ("video", solo.name) in kinds
    series_rows = [i for i in items if i["type"] == "series"]
    assert len(series_rows) == 1
    assert series_rows[0]["name"] == "Romans"
    assert series_rows[0]["count"] == 4
    assert series_rows[0]["url"] == series.get_absolute_url()
    # the flooded episodes do not also appear as individual cards
    video_names = [i["name"] for i in items if i["type"] == "video"]
    assert all(v.name not in video_names for v in flood)


def test_two_videos_from_one_series_do_not_collapse():
    series = SeriesFactory()
    pair = [VideoFactory(date_recorded=datetime.date(2026, 6, 10)) for _ in range(2)]
    series.videos.add(*pair)

    items = feed()["groups"][0]["items"]

    assert [i["type"] for i in items] == ["video", "video"]


def test_a_video_in_two_flooding_series_is_collapsed_only_once():
    big = SeriesFactory(name="Big series")
    small = SeriesFactory(name="Small series")
    shared = VideoFactory(date_recorded=datetime.date(2026, 6, 10))
    big_only = [VideoFactory(date_recorded=datetime.date(2026, 6, 10)) for _ in range(3)]
    small_only = [VideoFactory(date_recorded=datetime.date(2026, 6, 10)) for _ in range(2)]
    big.videos.add(shared, *big_only)
    small.videos.add(shared, *small_only)

    items = feed()["groups"][0]["items"]

    # shared goes to the bigger flood; small (2 remaining) stays under threshold
    series_rows = [i for i in items if i["type"] == "series"]
    assert [r["name"] for r in series_rows] == ["Big series"]
    assert series_rows[0]["count"] == 4
    video_names = [i["name"] for i in items if i["type"] == "video"]
    assert sorted(video_names) == sorted(v.name for v in small_only)


def test_series_row_sits_at_its_newest_episode_position():
    series = SeriesFactory(name="Flooding series")
    series.videos.add(
        *[VideoFactory(date_recorded=datetime.date(2026, 6, 8)) for _ in range(3)],
    )
    VideoFactory(name="Newer solo", date_recorded=datetime.date(2026, 6, 10))

    items = feed()["groups"][0]["items"]

    assert items[0]["name"] == "Newer solo"
    assert items[1]["type"] == "series"


def test_livestreams_are_excluded():
    VideoFactory(is_livestream=True, date_recorded=datetime.date(2026, 6, 10))

    assert feed()["groups"] == []


def test_pagination_flags_survive():
    for n in range(30):  # more than one 24-video page
        VideoFactory(date_recorded=datetime.date(2026, 6, 10) - datetime.timedelta(days=n))

    first, second = feed(page=1), feed(page=2)

    assert first["has_next_page"] and not first["has_prev_page"]
    assert second["has_prev_page"] and not second["has_next_page"]


def test_latest_page_serves_the_feed(client):
    """Feature-level: /latest/ renders the LatestFeed component with grouped
    props."""
    series = SeriesFactory(name="Acts")
    series.videos.add(*[VideoFactory(date_recorded=datetime.date(2024, 10, 2)) for _ in range(3)])

    page = inertia_page(client.get("/latest/"))

    assert page["component"] == "LatestFeed"
    groups = page["props"]["groups"]
    assert groups[0]["label"] == "October 2024"
    assert groups[0]["items"][0]["type"] == "series"


def test_feed_query_count_does_not_grow_with_catalogue_size(client, django_assert_max_num_queries):
    series = SeriesFactory()
    series.videos.add(*[VideoFactory(date_recorded=datetime.date(2026, 6, 10)) for _ in range(5)])
    for n in range(40):
        VideoFactory(date_recorded=datetime.date(2026, 5, 1) - datetime.timedelta(days=n))

    # +1 for the constant global "live now" nav flag (Inertia middleware).
    with django_assert_max_num_queries(7):
        client.get("/latest/")
