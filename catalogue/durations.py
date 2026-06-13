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
"""

import os
import re
import time

import requests

from catalogue.models import Video

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


def harvest_durations(session=None, refresh=False, vimeo_delay=VIMEO_DELAY):
    session = session or requests.Session()
    targets = Video.objects.all() if refresh else Video.objects.filter(duration_seconds__isnull=True)

    youtube, vimeo, unresolved = {}, [], []
    for video in targets.only("id", "url"):
        yid = youtube_id(video.url)
        if yid:
            youtube[yid] = video.id
        elif "vimeo.com" in (video.url or ""):
            vimeo.append(video)

    stats = {"youtube": 0, "vimeo": 0, "unresolved": 0}

    # YouTube: batch the ids
    yids = list(youtube)
    for start in range(0, len(yids), YT_BATCH):
        batch = yids[start : start + YT_BATCH]
        data = session.get(
            YT_API,
            params={"part": "contentDetails", "id": ",".join(batch), "key": os.environ["YOUTUBE_API_KEY"]},
            timeout=20,
        ).json()
        for item in data.get("items", []):
            seconds = parse_iso8601_duration(item.get("contentDetails", {}).get("duration"))
            if seconds is not None:
                Video.objects.filter(id=youtube[item["id"]]).update(duration_seconds=seconds)
                stats["youtube"] += 1

    # Vimeo: oEmbed per video
    for video in vimeo:
        response = session.get(VIMEO_OEMBED, params={"url": video.url}, timeout=15)
        seconds = response.json().get("duration") if response.status_code == 200 else None
        if seconds:
            Video.objects.filter(id=video.id).update(duration_seconds=int(seconds))
            stats["vimeo"] += 1
        else:
            unresolved.append(video.id)
        if vimeo_delay:
            time.sleep(vimeo_delay)

    stats["unresolved"] = len(unresolved)
    return stats
