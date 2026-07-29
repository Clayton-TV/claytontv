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

A platform that times out or errors is logged and skipped, never fatal:
those videos keep their null duration and the next run picks them up.
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


def _harvest_youtube(session, videos_by_yid, stats):
    """videos.list, 50 ids a call. A batch we can't reach is logged and
    skipped — its videos keep their null duration for the next run."""
    yids = list(videos_by_yid)
    for start in range(0, len(yids), YT_BATCH):
        batch = yids[start : start + YT_BATCH]
        try:
            response = session.get(
                YT_API,
                params={"part": "contentDetails", "id": ",".join(batch), "key": os.environ["YOUTUBE_API_KEY"]},
                timeout=20,
            )
        except requests.RequestException as exc:
            logger.warning("YouTube batch of %d videos failed — skipped until the next run: %s", len(batch), exc)
            stats["failed"] += len(batch)
            continue
        for item in response.json().get("items", []):
            seconds = parse_iso8601_duration(item.get("contentDetails", {}).get("duration"))
            if seconds is not None:
                Video.objects.filter(id=videos_by_yid[item["id"]]).update(duration_seconds=seconds)
                stats["youtube"] += 1


def _harvest_vimeo(session, videos, stats, delay):
    """oEmbed, one call a video. A video we can't reach is logged and
    skipped — the run carries on to the rest of the queue."""
    for video in videos:
        try:
            response = session.get(VIMEO_OEMBED, params={"url": video.url}, timeout=15)
        except requests.RequestException as exc:
            logger.warning("Vimeo request failed for %s — skipped until the next run: %s", video.url, exc)
            stats["failed"] += 1
        else:
            seconds = response.json().get("duration") if response.status_code == 200 else None
            if seconds:
                Video.objects.filter(id=video.id).update(duration_seconds=int(seconds))
                stats["vimeo"] += 1
            else:
                stats["unresolved"] += 1
        if delay:
            time.sleep(delay)


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

    # unresolved: the platform answered but had no duration for us.
    # failed: we couldn't reach the platform — the next run retries those.
    stats = {"youtube": 0, "vimeo": 0, "unresolved": 0, "failed": 0}
    _harvest_youtube(session, youtube, stats)
    _harvest_vimeo(session, vimeo, stats, vimeo_delay)
    return stats
