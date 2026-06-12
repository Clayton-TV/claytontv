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
