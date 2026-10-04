"""Harvest video runtimes from the hosting platforms.

Two gentle, auth-light sources — never the dying legacy server:
- YouTube: videos.list contentDetails.duration (ISO-8601), batched 50/call,
  1 quota unit each (~82 calls for the whole catalogue).
- Vimeo: oEmbed (no auth), per video. Resolves when the URL carries its
  privacy hash or the video is public; the rest stay null until re-synced
  or the Vimeo token lands.

Swappable by design: the source is keyed off the URL platform and the
YouTube key comes from the environment. Idempotent — only fills nulls
unless refresh=True.

Provider failures and malformed responses are logged, counted and skipped so
the remaining queue can still be harvested.
"""

import logging
import os
import re
import time

import requests

from catalogue.models import Video

logger = logging.getLogger(__name__)

YT_API = "https://youtube.googleapis.com/youtube/v3/videos"
VIMEO_OEMBED = "https://vimeo.com/api/oembed.json"
YT_BATCH = 50
VIMEO_DELAY = 0.2  # polite pacing for the per-video oEmbed calls

# duration_seconds is a PositiveIntegerField: anything outside this range is a
# CHECK-constraint or integer-overflow error on Postgres, which SQLite hides.
MAX_DURATION = 2**31 - 1

_YT_ID = re.compile(r"(?:youtu\.be/|v/|embed/|watch\?v=|&v=)([^#&?/]+)")
_ISO = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def parse_iso8601_duration(value):
    """'PT28M50S' → 1730. Returns None for empty/malformed input. 'P0D'
    (zero-length, used for some live placeholders) → 0."""
    if not value:
        return None
    if value == "P0D":
        return 0
    match = _ISO.match(value)
    if not match or value == "PT":
        return None
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def format_duration(seconds):
    """Whole seconds → 'h:mm:ss' or 'm:ss'. Empty string for None."""
    if seconds is None:
        return ""
    hours, rem = divmod(int(seconds), 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def youtube_id(url):
    match = _YT_ID.search(url or "")
    return match.group(1) if match else None


def storable_duration(value):
    """Whole seconds we're willing to write, or None if the platform sent
    something the column can't hold. `bool` is excluded deliberately: it is a
    subclass of int, so True would otherwise store a 1-second runtime."""
    if isinstance(value, bool):
        return None
    try:
        seconds = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return seconds if 0 <= seconds <= MAX_DURATION else None


def _harvest_youtube(session, youtube, stats):
    yids = list(youtube)
    key = os.environ.get("YOUTUBE_API_KEY")
    if yids and not key:
        logger.warning("YOUTUBE_API_KEY not set — %d YouTube videos skipped", len(yids))
    for start in range(0, len(yids) if key else 0, YT_BATCH):
        batch = yids[start : start + YT_BATCH]
        try:
            response = session.get(
                YT_API,
                params={"part": "contentDetails", "id": ",".join(batch), "key": key},
                timeout=20,
            )
            payload = response.json() if response.status_code == 200 else None
        except (requests.RequestException, ValueError) as exc:
            logger.warning("YouTube batch failed (%s): %s", ",".join(batch), type(exc).__name__)
            stats["failed"] += len(batch)
            continue
        items = payload.get("items") if isinstance(payload, dict) else None
        if not isinstance(items, list):
            logger.warning("YouTube returned %s for batch (%s)", response.status_code, ",".join(batch))
            stats["failed"] += len(batch)
            continue
        answered = set()
        for item in items:
            yid = item.get("id") if isinstance(item, dict) else None
            if not isinstance(yid, str) or yid not in batch:
                logger.warning("YouTube returned an unusable item")
                continue
            answered.add(yid)
            try:
                seconds = storable_duration(parse_iso8601_duration(item.get("contentDetails", {}).get("duration")))
            except (AttributeError, TypeError, ValueError):
                logger.warning("YouTube sent unreadable content details for %s", yid)
                stats["failed"] += 1
            else:
                if seconds is None:
                    stats["unresolved"] += 1
                else:
                    Video.objects.filter(id=youtube[yid]).update(duration_seconds=seconds)
                    stats["youtube"] += 1
        stats["unresolved"] += len(set(batch) - answered)


def _harvest_vimeo(session, vimeo, stats, vimeo_delay):
    for video in vimeo:
        try:
            response = session.get(VIMEO_OEMBED, params={"url": video.url}, timeout=15)
            payload = response.json() if response.status_code == 200 else None
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Vimeo request failed for video %s: %s", video.id, type(exc).__name__)
            stats["failed"] += 1
        else:
            if response.status_code in (404, 410):
                stats["unresolved"] += 1
            elif response.status_code != 200 or not isinstance(payload, dict):
                logger.warning("Vimeo returned %s for video %s", response.status_code, video.id)
                stats["failed"] += 1
            elif payload.get("duration") is None:
                stats["unresolved"] += 1
            else:
                seconds = storable_duration(payload["duration"])
                if seconds is None:
                    logger.warning("Vimeo sent an unusable duration for video %s", video.id)
                    stats["failed"] += 1
                else:
                    Video.objects.filter(id=video.id).update(duration_seconds=seconds)
                    stats["vimeo"] += 1
        if vimeo_delay:
            time.sleep(vimeo_delay)


def harvest_durations(session=None, refresh=False, vimeo_delay=VIMEO_DELAY):
    session = session or requests.Session()
    targets = Video.objects.all() if refresh else Video.objects.filter(duration_seconds__isnull=True)

    youtube, vimeo = {}, []
    for video in targets.only("id", "url"):
        yid = youtube_id(video.url)
        if yid:
            youtube[yid] = video.id
        elif "vimeo.com" in (video.url or ""):
            vimeo.append(video)

    stats = {"youtube": 0, "vimeo": 0, "unresolved": 0, "failed": 0}
    _harvest_youtube(session, youtube, stats)
    _harvest_vimeo(session, vimeo, stats, vimeo_delay)
    if stats["failed"] and not (stats["youtube"] or stats["vimeo"] or stats["unresolved"]):
        logger.error("Duration harvest failed for every attempted lookup")
    return stats
