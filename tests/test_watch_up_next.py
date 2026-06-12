import pytest

from tests.factories import SeriesFactory, VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_up_next_is_deferred_not_in_first_load(client):
    """The watch page must paint without waiting on the series rail: up_next
    arrives via the Inertia deferred-props follow-up request."""
    video = VideoFactory()

    page = inertia_page(client.get(f"/video/{video.id}"))

    assert "up_next" not in page["props"]
    assert "up_next" in page.get("deferredProps", {}).get("default", [])


def test_up_next_returns_other_videos_from_the_same_series(client):
    series = SeriesFactory(name="John's Gospel")
    current = VideoFactory(name="Episode 2")
    sibling = VideoFactory(name="Episode 1")
    series.videos.add(current, sibling)

    response = client.get(
        f"/video/{current.id}",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="WatchVideo",
        HTTP_X_INERTIA_PARTIAL_DATA="up_next",
    )

    props = response.json()["props"]
    assert props["up_next"]["series"]["name"] == "John's Gospel"
    names = [v["name"] for v in props["up_next"]["videos"]]
    assert names == ["Episode 1"]
    assert "Episode 2" not in names


def test_up_next_is_null_when_video_has_no_series(client):
    video = VideoFactory()

    response = client.get(
        f"/video/{video.id}",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="WatchVideo",
        HTTP_X_INERTIA_PARTIAL_DATA="up_next",
    )

    assert response.json()["props"]["up_next"] is None


def fetch_up_next(client, video):
    response = client.get(
        f"/video/{video.id}",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="WatchVideo",
        HTTP_X_INERTIA_PARTIAL_DATA="up_next",
    )
    return response.json()["props"]["up_next"]


def test_up_next_names_the_next_episode_in_course_order(client):
    """Autoplay-next follows the same order the series page shows: episode
    number first, then date — not newest-first."""
    series = SeriesFactory()
    one = VideoFactory(name="Part 1", number_in_series=1)
    two = VideoFactory(name="Part 2", number_in_series=2)
    three = VideoFactory(name="Part 3", number_in_series=3)
    series.videos.add(one, two, three)

    assert fetch_up_next(client, two)["next"]["name"] == "Part 3"
    assert fetch_up_next(client, one)["next"]["name"] == "Part 2"


def test_up_next_next_is_null_for_the_final_episode(client):
    series = SeriesFactory()
    one = VideoFactory(name="Part 1", number_in_series=1)
    two = VideoFactory(name="Part 2", number_in_series=2)
    series.videos.add(one, two)

    assert fetch_up_next(client, two)["next"] is None


def test_up_next_falls_back_to_date_order_when_numbers_are_missing(client):
    """Legacy series often have no number_in_series at all; the next episode
    is then the next-recorded one."""
    import datetime

    series = SeriesFactory()
    older = VideoFactory(name="Older", date_recorded=datetime.date(2024, 1, 1))
    newer = VideoFactory(name="Newer", date_recorded=datetime.date(2024, 2, 1))
    series.videos.add(older, newer)

    assert fetch_up_next(client, older)["next"]["name"] == "Newer"
    assert fetch_up_next(client, newer)["next"] is None
