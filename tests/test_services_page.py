"""The Services destination (/livestreams) — live now + upcoming services +
past-services archive in one place — and the global "live now" nav flag.
Elderly-critical: one obvious place for Sunday's service."""

import datetime

import pytest

from catalogue.models import LiveStream
from tests.factories import VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_services_page_shows_live_upcoming_and_past(client):
    LiveStream.objects.create(
        video_id="liveNow1234",
        title="Morning Service",
        channel_id="UC1",
        channel_title="Jesmond",
        status="live",
        actual_start=datetime.datetime(2026, 6, 14, 10, 30, tzinfo=datetime.UTC),
    )
    LiveStream.objects.create(
        video_id="upNext56789",
        title="Evening Service",
        channel_id="UC1",
        status="upcoming",
        scheduled_start=datetime.datetime(2099, 1, 1, tzinfo=datetime.UTC),
    )
    VideoFactory(is_livestream=True, name="Old recorded service")
    VideoFactory(is_livestream=False, name="A regular sermon")

    page = inertia_page(client.get("/livestreams/"))
    props = page["props"]

    assert page["component"] == "Services"
    assert [s["video_id"] for s in props["live"]] == ["liveNow1234"]
    assert props["live"][0]["url"] == "https://www.youtube.com/watch?v=liveNow1234"
    assert [s["title"] for s in props["upcoming"]] == ["Evening Service"]
    past_names = [v["name"] for v in props["past"]]
    assert "Old recorded service" in past_names
    assert "A regular sermon" not in past_names


def test_services_page_is_quiet_when_nothing_is_on(client):
    VideoFactory(is_livestream=True, name="Old service")

    props = inertia_page(client.get("/livestreams/"))["props"]

    assert props["live"] == []
    assert props["upcoming"] == []
    assert len(props["past"]) == 1


def test_upcoming_excludes_past_schedules(client):
    LiveStream.objects.create(
        video_id="past1234567",
        title="Past",
        channel_id="UC1",
        status="upcoming",
        scheduled_start=datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC),
    )

    assert inertia_page(client.get("/livestreams/"))["props"]["upcoming"] == []


def test_live_now_nav_flag_reflects_a_live_broadcast(client):
    assert inertia_page(client.get("/"))["props"].get("live_now") in (False, None)

    LiveStream.objects.create(video_id="liveNow1234", title="x", channel_id="UC1", status="live")

    assert inertia_page(client.get("/"))["props"]["live_now"] is True
