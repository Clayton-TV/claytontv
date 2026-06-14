"""Fetch a video's metadata from its hosting platform, for the Studio's
paste-a-URL intake (Epic 3, Slice 3).

Given a YouTube or Vimeo URL we return a small normalised dict — title,
description, thumbnail, runtime, recorded date — that the editor previews and
confirms before saving. Deliberately reuses the existing, battle-tested helpers
rather than growing new API clients:

- YouTube: ``youtube_live.api_get`` (the retrying ``videos.list`` client; 1
  quota unit) + ``durations.parse_iso8601_duration``.
- Vimeo: the public oEmbed endpoint (no auth), same source ``harvest_durations``
  already uses for runtimes.

Network failures / unknown URLs raise ``MetadataError`` with a human-readable
message; the view turns that into a friendly inline error.
"""

import requests

from catalogue import durations, youtube_live

VIMEO_OEMBED = "https://vimeo.com/api/oembed.json"


class MetadataError(Exception):
    """A URL we can't turn into video metadata (unsupported host, not found,
    or the platform API failed). The message is safe to show an editor."""


def fetch_metadata(url, session=None):
    """Normalised metadata for a YouTube/Vimeo ``url``.

    Returns a dict: ``platform``, ``platform_id``, ``url`` (canonical),
    ``name``, ``description``, ``thumbnail``, ``duration_seconds``,
    ``date_recorded`` (``YYYY-MM-DD`` or None). Raises ``MetadataError`` for an
    unsupported URL or a failed fetch.
    """
    url = (url or "").strip()
    if not url:
        raise MetadataError("Paste a video URL to get started.")

    session = session or requests.Session()

    if durations.youtube_id(url):
        return _fetch_youtube(url, session)
    if "vimeo.com" in url:
        return _fetch_vimeo(url, session)
    raise MetadataError("That doesn't look like a YouTube or Vimeo link.")


def _fetch_youtube(url, session):
    yid = durations.youtube_id(url)
    try:
        data = youtube_live.api_get(session, "videos", part="snippet,contentDetails", id=yid)
    except youtube_live.YoutubeApiError as exc:
        raise MetadataError("Couldn't reach YouTube just now — try again in a moment.") from exc
    except KeyError as exc:  # YOUTUBE_API_KEY not configured in this environment
        raise MetadataError("YouTube lookups aren't configured here — try a Vimeo link.") from exc

    items = data.get("items") or []
    if not items:
        raise MetadataError("No YouTube video found at that link (it may be private or deleted).")

    snippet = items[0].get("snippet", {})
    details = items[0].get("contentDetails", {})
    published = snippet.get("publishedAt") or ""
    return {
        "platform": "youtube",
        "platform_id": yid,
        "url": f"https://www.youtube.com/watch?v={yid}",
        "name": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "thumbnail": _best_youtube_thumbnail(snippet.get("thumbnails", {})),
        "duration_seconds": durations.parse_iso8601_duration(details.get("duration")),
        "date_recorded": published[:10] or None,
    }


def _best_youtube_thumbnail(thumbnails):
    """Highest-resolution thumbnail YouTube offers for this video."""
    for size in ("maxres", "standard", "high", "medium", "default"):
        if size in thumbnails:
            return thumbnails[size].get("url")
    return None


def _fetch_vimeo(url, session):
    try:
        response = session.get(VIMEO_OEMBED, params={"url": url}, timeout=15)
    except requests.RequestException as exc:
        raise MetadataError("Couldn't reach Vimeo just now — try again in a moment.") from exc
    if response.status_code != 200:
        raise MetadataError("No Vimeo video found at that link (it may be private or deleted).")

    data = response.json()
    platform_id = str(data.get("video_id") or "")
    duration = data.get("duration")
    upload_date = data.get("upload_date") or ""  # "2014-05-30 12:00:00"
    return {
        "platform": "vimeo",
        "platform_id": platform_id,
        "url": f"https://vimeo.com/{platform_id}" if platform_id else url,
        "name": data.get("title", ""),
        "description": data.get("description", "") or "",
        "thumbnail": data.get("thumbnail_url"),
        "duration_seconds": int(duration) if duration else None,
        "date_recorded": upload_date[:10] or None,
    }
