"""Live & upcoming broadcast sync from the YouTube Data API (Epic 4 MVP).

Quota discipline shapes everything here: search.list costs 100 units per
call against a 10,000/day default quota, while videos.list costs 1. So
broadcast *discovery* (search) is meant to run hourly, and cheap status
*refreshes* (videos.list on known ids) every few minutes — see the
sync_live_streams management command.

Channels are not configured anywhere: they're discovered from the
catalogue's own recent livestream videos, so whoever actually streams for
Clayton TV is who gets watched.
"""

import os
import re
import time
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from catalogue.models import LiveStream, Video

API_BASE = "https://youtube.googleapis.com/youtube/v3"
STARTS_SOON_WINDOW = timedelta(minutes=30)
CHANNEL_SAMPLE = 50  # recent livestream videos to derive channels from
SEARCH_RESULTS_PER_TYPE = 10

YOUTUBE_ID_REGEX = re.compile(r"(?:youtu\.be/|v/|embed/|watch\?v=|&v=)([^#&?/]+)")


RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 3


class YoutubeApiError(RuntimeError):
    pass


def api_get(session, endpoint, **params):
    """GET with retries: YouTube intermittently 403s requests from
    datacenter IPs ("cannot act on behalf of the specified Google account"
    — observed ~1 in 3 from app03 with a valid, unrestricted-IP key)."""
    params["key"] = os.environ["YOUTUBE_API_KEY"]
    response = None
    for attempt in range(RETRY_ATTEMPTS):
        if attempt:
            time.sleep(RETRY_DELAY_SECONDS * attempt)
        response = session.get(f"{API_BASE}/{endpoint}", params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
    raise YoutubeApiError(f"{endpoint} returned {response.status_code}: {getattr(response, 'text', '')[:300]}")


def youtube_id(url):
    match = YOUTUBE_ID_REGEX.search(url or "")
    return match.group(1) if match else None


def discover_channels(session):
    """Distinct channel ids behind our most recent livestream recordings.
    One videos.list call (1 quota unit) for up to 50 ids."""
    recent = Video.objects.filter(is_livestream=True).order_by("-date_recorded")[: CHANNEL_SAMPLE * 2]
    ids = [vid for v in recent if (vid := youtube_id(v.url))][:CHANNEL_SAMPLE]
    if not ids:
        return []
    data = api_get(session, "videos", part="snippet", id=",".join(ids), maxResults=50)
    return sorted({item["snippet"]["channelId"] for item in data.get("items", [])})


def discover_broadcasts(session, channel_ids):
    """Find live and scheduled broadcasts per channel (search.list, 100 units
    per call — run hourly, not per minute) and upsert LiveStream rows. Ends
    with a status refresh so times and states are correct immediately."""
    found = 0
    for channel_id in channel_ids:
        for event_type in ("live", "upcoming"):
            # No order param: eventType+order=date 403s from some server
            # regions ("cannot act on behalf of the specified Google
            # account" — observed from app03, fine from a UK residential
            # IP). Default relevance order is fine for ≤10 broadcasts.
            data = api_get(
                session,
                "search",
                part="snippet",
                channelId=channel_id,
                eventType=event_type,
                type="video",
                maxResults=SEARCH_RESULTS_PER_TYPE,
            )
            for item in data.get("items", []):
                snippet = item["snippet"]
                thumbnails = snippet.get("thumbnails") or {}
                thumbnail = (thumbnails.get("high") or thumbnails.get("default") or {}).get("url")
                LiveStream.objects.update_or_create(
                    video_id=item["id"]["videoId"],
                    defaults={
                        "channel_id": snippet["channelId"],
                        "channel_title": snippet.get("channelTitle", ""),
                        "title": snippet["title"],
                        "thumbnail": thumbnail,
                        "status": event_type,
                    },
                )
                found += 1
    refresh_statuses(session)
    return found


def refresh_statuses(session):
    """Cheap (1 unit) state pass over every non-ended broadcast: fill in
    scheduled/actual times and walk upcoming → live → ended. Broadcasts that
    vanish from the API (deleted/private) are marked ended — never leave a
    ghost LIVE banner."""
    active = list(LiveStream.objects.exclude(status="ended"))
    if not active:
        return 0
    data = api_get(
        session,
        "videos",
        part="snippet,liveStreamingDetails",
        id=",".join(s.video_id for s in active),
        maxResults=50,
    )
    seen = {}
    for item in data.get("items", []):
        seen[item["id"]] = item
    for stream in active:
        item = seen.get(stream.video_id)
        if item is None:
            stream.status = "ended"
            stream.save()
            continue
        details = item.get("liveStreamingDetails", {})
        stream.title = item["snippet"].get("title", stream.title)
        stream.scheduled_start = _parse(details.get("scheduledStartTime")) or stream.scheduled_start
        stream.actual_start = _parse(details.get("actualStartTime")) or stream.actual_start
        stream.actual_end = _parse(details.get("actualEndTime")) or stream.actual_end
        if stream.actual_end:
            stream.status = "ended"
        elif stream.actual_start:
            stream.status = "live"
        else:
            stream.status = "upcoming"
        stream.save()
    return len(active)


def _parse(value):
    return parse_datetime(value) if value else None


def _serialize_live(stream):
    return {
        "video_id": stream.video_id,
        "title": stream.title,
        "url": stream.url,
        "thumbnail": stream.thumbnail,
        "channel": stream.channel_title,
    }


def _serialize_upcoming(stream):
    return {
        "video_id": stream.video_id,
        "title": stream.title,
        "url": stream.url,
        "channel": stream.channel_title,
        "scheduled_start": stream.scheduled_start,
        # Inside the pre-service window the card embeds the stream's waiting
        # room (countdown; starts by itself when live) instead of a static
        # schedule.
        "starts_soon": stream.scheduled_start <= timezone.now() + STARTS_SOON_WINDOW,
    }


def live_streams():
    return [_serialize_live(s) for s in LiveStream.objects.filter(status="live").order_by("-actual_start")]


def upcoming_streams():
    return [
        _serialize_upcoming(s)
        for s in LiveStream.objects.filter(status="upcoming", scheduled_start__gte=timezone.now()).order_by(
            "scheduled_start"
        )
    ]


def is_live_now():
    """Cheap existence check for the global "live" nav indicator."""
    return LiveStream.objects.filter(status="live").exists()


def homepage_live_props():
    """What the homepage hero slot needs: anything live right now, and the
    next scheduled service."""
    upcoming = upcoming_streams()
    return live_streams(), (upcoming[0] if upcoming else None)
