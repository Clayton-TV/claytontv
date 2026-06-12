"""YouTube live/upcoming broadcast sync (Epic 4 MVP).

Quota discipline shapes the design: search.list costs 100 units per call, so
broadcast *discovery* runs hourly (--discover), while cheap status
*refreshes* (videos.list, 1 unit) can run every few minutes. Channels are
discovered from the catalogue's own recent livestream videos — the legacy
Channel table is empty, so nothing is hardcoded.
"""

import datetime

import pytest

from catalogue.models import LiveStream
from catalogue.youtube_live import discover_broadcasts, discover_channels, refresh_statuses
from tests.factories import VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


class FakeSession:
    """Canned YouTube API responses keyed by endpoint."""

    def __init__(self, by_endpoint):
        self.by_endpoint = by_endpoint
        self.calls = []

    def get(self, url, params=None, timeout=None):
        endpoint = url.rstrip("/").split("/")[-1]
        self.calls.append((endpoint, params))

        class Response:
            status_code = 200

            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        payload = self.by_endpoint[endpoint]
        return Response(payload(params) if callable(payload) else payload)


def video_item(video_id, channel="UCjesmond", scheduled=None, started=None, ended=None):
    details = {}
    if scheduled:
        details["scheduledStartTime"] = scheduled
    if started:
        details["actualStartTime"] = started
    if ended:
        details["actualEndTime"] = ended
    return {
        "id": video_id,
        "snippet": {"title": f"Service {video_id}", "channelId": channel, "channelTitle": "Jesmond", "thumbnails": {}},
        "liveStreamingDetails": details,
    }


def test_channels_are_discovered_from_recent_catalogue_livestreams(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    VideoFactory(is_livestream=True, url="https://www.youtube.com/watch?v=aaa111aaa11")
    VideoFactory(is_livestream=True, url="https://www.youtube.com/watch?v=bbb222bbb22")
    VideoFactory(is_livestream=False, url="https://www.youtube.com/watch?v=ccc333ccc33")  # not sampled

    session = FakeSession(
        {
            "videos": lambda params: {
                "items": [
                    {"id": "aaa111aaa11", "snippet": {"channelId": "UCjesmond"}},
                    {"id": "bbb222bbb22", "snippet": {"channelId": "UCother"}},
                ]
            }
        }
    )

    channels = discover_channels(session)

    assert channels == ["UCjesmond", "UCother"]
    endpoint, params = session.calls[0]
    assert endpoint == "videos"
    assert "ccc333ccc33" not in params["id"]


def search_item(video_id, title, thumbnails=None):
    snippet = {"title": title, "channelId": "UCjesmond", "channelTitle": "Jesmond", "thumbnails": thumbnails or {}}
    return {"id": {"videoId": video_id}, "snippet": snippet}


def test_discover_broadcasts_upserts_live_and_upcoming(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    search_payloads = {
        "live": {
            "items": [search_item("liveNow1234", "Morning Service", {"high": {"url": "https://i.ytimg.com/x.jpg"}})]
        },
        "upcoming": {"items": [search_item("upNext56789", "Evening Service")]},
    }
    session = FakeSession(
        {
            "search": lambda params: search_payloads[params["eventType"]],
            "videos": lambda params: {
                "items": [
                    video_item("liveNow1234", started="2026-06-14T10:30:00Z"),
                    video_item("upNext56789", scheduled="2026-06-14T18:30:00Z"),
                ]
            },
        }
    )

    discover_broadcasts(session, ["UCjesmond"])

    live = LiveStream.objects.get(video_id="liveNow1234")
    assert live.status == "live"
    upcoming = LiveStream.objects.get(video_id="upNext56789")
    assert upcoming.status == "upcoming"
    assert upcoming.scheduled_start.isoformat().startswith("2026-06-14T18:30")

    # Idempotent: run again, still two rows
    discover_broadcasts(session, ["UCjesmond"])
    assert LiveStream.objects.count() == 2


def test_refresh_transitions_upcoming_to_live_to_ended(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    LiveStream.objects.create(video_id="vid12345678", title="Service", channel_id="UC1", status="upcoming")

    live_session = FakeSession({"videos": {"items": [video_item("vid12345678", started="2026-06-14T10:30:00Z")]}})
    refresh_statuses(live_session)
    assert LiveStream.objects.get(video_id="vid12345678").status == "live"

    ended_session = FakeSession(
        {"videos": {"items": [video_item("vid12345678", started="2026-06-14T10:30:00Z", ended="2026-06-14T11:45:00Z")]}}
    )
    refresh_statuses(ended_session)
    assert LiveStream.objects.get(video_id="vid12345678").status == "ended"


def test_refresh_marks_vanished_broadcasts_ended(monkeypatch):
    """Deleted/private broadcasts disappear from videos.list — never leave a
    ghost LIVE banner on the homepage."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    LiveStream.objects.create(video_id="gone1234567", title="Service", channel_id="UC1", status="live")

    refresh_statuses(FakeSession({"videos": {"items": []}}))

    assert LiveStream.objects.get(video_id="gone1234567").status == "ended"


def test_refresh_with_nothing_active_makes_no_api_call(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    LiveStream.objects.create(video_id="done1234567", title="Service", channel_id="UC1", status="ended")
    session = FakeSession({})

    refresh_statuses(session)

    assert session.calls == []


def test_homepage_serves_live_and_next_service(client):
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
        scheduled_start=datetime.datetime(2099, 6, 14, 18, 30, tzinfo=datetime.UTC),
    )
    LiveStream.objects.create(video_id="old12345678", title="Old", channel_id="UC1", status="ended")

    props = inertia_page(client.get("/"))["props"]

    assert [s["video_id"] for s in props["livestreams"]] == ["liveNow1234"]
    assert props["livestreams"][0]["url"] == "https://www.youtube.com/watch?v=liveNow1234"
    assert props["next_service"]["title"] == "Evening Service"


def test_homepage_next_service_ignores_past_schedules(client):
    LiveStream.objects.create(
        video_id="past1234567",
        title="Past",
        channel_id="UC1",
        status="upcoming",
        scheduled_start=datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC),
    )

    props = inertia_page(client.get("/"))["props"]

    assert props["next_service"] is None
