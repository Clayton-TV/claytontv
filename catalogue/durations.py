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
    key = os.environ.get("YOUTUBE_API_KEY")
    if yids and not key:
        logger.warning("YOUTUBE_API_KEY not set — %d YouTube videos skipped until the next run", len(yids))
        stats["failed"] += len(yids)
        return

    for start in range(0, len(yids), YT_BATCH):
        batch = yids[start : start + YT_BATCH]
        try:
            response = session.get(
                YT_API,
                params={"part": "contentDetails", "id": ",".join(batch), "key": key},
                timeout=20,
            )
            payload = response.json() if response.status_code == 200 else None
        except (requests.RequestException, ValueError) as exc:
            logger.warning("YouTube batch failed (%s) — skipped until the next run: %s", ",".join(batch), exc)
            stats["failed"] += len(batch)
            continue
        items = payload.get("items", []) if isinstance(payload, dict) else None
        if not isinstance(items, list):
            logger.warning(
                "YouTube returned %s for batch (%s) — skipped until the next run", response.status_code, ",".join(batch)
            )
            stats["failed"] += len(batch)
            continue
        answered = set()
        for item in items:
            yid = item.get("id") if isinstance(item, dict) else None
            if not isinstance(yid, str) or yid not in videos_by_yid:
                # A 200 whose item has no usable id tells us nothing about which
                # video it belongs to. Count it and carry on; indexing it would
                # have killed the whole run.
                logger.warning("YouTube returned an unusable item, skipped: %r", item)
                stats["failed"] += 1
                continue
            answered.add(yid)
            try:
                seconds = parse_iso8601_duration(item.get("contentDetails", {}).get("duration"))
            except (AttributeError, TypeError):
                logger.warning("YouTube sent an unreadable contentDetails for %s, skipped: %r", yid, item)
                stats["failed"] += 1
                continue
            if seconds is not None:
                Video.objects.filter(id=videos_by_yid[yid]).update(duration_seconds=seconds)
                stats["youtube"] += 1
            else:
                stats["unresolved"] += 1

        # videos.list quietly drops ids it won't serve (deleted, private,
        # region-blocked) from an otherwise-clean 200. Unbucketed they vanished
        # from the totals altogether, so the stats stopped summing to the queue.
        missing = [yid for yid in batch if yid not in answered]
        if missing:
            logger.warning(
                "YouTube returned no item for %d of %d ids (%s) — left unresolved",
                len(missing),
                len(batch),
                ",".join(missing),
            )
            stats["unresolved"] += len(missing)


def _record_vimeo_payload(video, payload, stats):
    """Sort one oEmbed 200 body into a bucket. Never raises — a malformed
    duration is a failure to count, not a reason to abandon the queue."""
    if not isinstance(payload, dict):
        logger.warning("Vimeo sent an unreadable body for %s — skipped until the next run: %r", video.url, payload)
        stats["failed"] += 1
        return
    seconds = payload.get("duration")
    if not seconds:
        # The documented hashless case: 200, but "duration": null. The platform
        # answered us, so this is unresolved rather than a failure.
        stats["unresolved"] += 1
        return
    try:
        resolved = int(seconds)
    except (TypeError, ValueError):
        logger.warning("Vimeo sent a non-numeric duration %r for %s — skipped until the next run", seconds, video.url)
        stats["failed"] += 1
        return
    Video.objects.filter(id=video.id).update(duration_seconds=resolved)
    stats["vimeo"] += 1


def _harvest_vimeo(session, videos, stats, delay):
    """oEmbed, one call a video. A video we can't reach is logged and
    skipped — the run carries on to the rest of the queue."""
    for video in videos:
        try:
            response = session.get(VIMEO_OEMBED, params={"url": video.url}, timeout=15)
            payload = response.json() if response.status_code == 200 else None
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Vimeo request failed for %s — skipped until the next run: %s", video.url, exc)
            stats["failed"] += 1
        else:
            if response.status_code != 200:
                # Matches the YouTube path: a non-200 is Vimeo rate-limiting us
                # or falling over, not a video that genuinely has no duration.
                logger.warning("Vimeo returned %s for %s — skipped until the next run", response.status_code, video.url)
                stats["failed"] += 1
            else:
                _record_vimeo_payload(video, payload, stats)
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

    # Alert when failures outweigh real successes. Two traps this avoids:
    # `unresolved` is not evidence of a healthy run — the hashless Vimeo
    # back-catalogue lands there on every single run (docs/DEPLOYMENT.md), so
    # counting it here suppressed the alert permanently; and demanding that we
    # resolved *nothing* never catches the realistic failure, quota exhaustion,
    # which is partial by nature. One slow video among successes stays a
    # warning. Sentry only raises an event at ERROR — WARNING is a breadcrumb.
    resolved = stats["youtube"] + stats["vimeo"]
    if stats["failed"] > resolved:
        logger.error(
            "Duration harvest failed on %d of the %d videos it could have resolved — left for the next run",
            stats["failed"],
            stats["failed"] + resolved,
        )
    return stats
