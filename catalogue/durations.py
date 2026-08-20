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

Nothing a platform sends is fatal: a timeout, a non-200, a malformed body or
an unstorable duration is logged, counted and skipped, and those videos keep
their null duration for the next run. A platform failing a serious share of
its own queue logs an ERROR, which is what raises a Sentry event.
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

# A platform is in trouble when it fails a quarter of its own queue, but never
# on fewer than this many videos — on a quiet night the queue is a handful of
# leftovers and one timeout is not an outage.
ALERT_FAILURE_RATE = 0.25
ALERT_MIN_FAILURES = 10

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
    except (TypeError, ValueError):
        return None
    return seconds if 0 <= seconds <= MAX_DURATION else None


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
                # video it belongs to — indexing it would have killed the run.
                # Not counted here: the id it was meant to answer is still in
                # `batch`, so the sweep below books it once, as unresolved.
                logger.warning("YouTube returned an unusable item, skipped: %r", item)
                continue
            answered.add(yid)
            try:
                seconds = storable_duration(parse_iso8601_duration(item.get("contentDetails", {}).get("duration")))
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
    """Sort one oEmbed 200 body into a bucket. A duration we can't store is a
    failure to count, not a reason to abandon the rest of the queue."""
    if not isinstance(payload, dict):
        logger.warning("Vimeo sent an unreadable body for %s — skipped until the next run: %r", video.url, payload)
        stats["failed"] += 1
        return
    raw = payload.get("duration")
    if not raw:
        # The hashless case: a 200 that simply carries no duration. The platform
        # answered us, so this is unresolved rather than a failure.
        stats["unresolved"] += 1
        return
    seconds = storable_duration(raw)
    if seconds is None:
        logger.warning("Vimeo sent an unusable duration %r for %s — skipped until the next run", raw, video.url)
        stats["failed"] += 1
        return
    Video.objects.filter(id=video.id).update(duration_seconds=seconds)
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
            if response.status_code in (404, 410):
                # Gone for good — deleted or private. Probing 40 random hashless
                # catalogue URLs found 8 of them in this state, so treating it
                # as a platform failure would have kept ~a fifth of the Vimeo
                # back-catalogue permanently in `failed` and fired the outage
                # alert every night, on every healthy run, until someone muted it.
                stats["unresolved"] += 1
            elif response.status_code != 200:
                # 429/5xx: Vimeo rate-limiting us or falling over. Worth
                # retrying, and worth counting towards the outage alert.
                logger.warning("Vimeo returned %s for %s — skipped until the next run", response.status_code, video.url)
                stats["failed"] += 1
            else:
                _record_vimeo_payload(video, payload, stats)
        if delay:
            time.sleep(delay)


def _new_stats():
    return {"youtube": 0, "vimeo": 0, "unresolved": 0, "failed": 0}


def _alert_if_a_platform_is_failing(platform, queued, failed):
    """Sentry only raises an event at ERROR; a warning is just a breadcrumb, so
    this is the line between "someone finds out" and "nobody does".

    Judged per platform against that platform's own queue. Pooling the two let
    a healthy YouTube — by far the bigger half — mask Vimeo being flat on its
    back. Judged on a share of the queue rather than "resolved nothing",
    because the realistic outage is a spent YouTube quota, which only kills the
    batches after it ran out. And never counting `unresolved`, which is not
    evidence of health: the deleted and hashless Vimeo videos land there on
    every single run.
    """
    if queued and failed >= max(ALERT_MIN_FAILURES, ALERT_FAILURE_RATE * queued):
        logger.error("%s duration harvest failed on %d of %d videos — left for the next run", platform, failed, queued)


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
    youtube_stats, vimeo_stats = _new_stats(), _new_stats()
    _harvest_youtube(session, youtube, youtube_stats)
    _harvest_vimeo(session, vimeo, vimeo_stats, vimeo_delay)

    _alert_if_a_platform_is_failing("YouTube", len(youtube), youtube_stats["failed"])
    _alert_if_a_platform_is_failing("Vimeo", len(vimeo), vimeo_stats["failed"])
    return {key: youtube_stats[key] + vimeo_stats[key] for key in youtube_stats}
