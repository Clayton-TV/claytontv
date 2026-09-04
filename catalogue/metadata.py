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

import re

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
    return _youtube_doc(yid, items[0])


def _youtube_doc(yid, item):
    """Normalise one ``videos.list`` item into our metadata dict."""
    snippet = item.get("snippet", {})
    details = item.get("contentDetails", {})
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


# --------------------------------------------------------------------------- #
# Bulk intake (Slice 5): many URLs at once + YouTube playlist expansion
# --------------------------------------------------------------------------- #

YT_BATCH = 50
_PLAYLIST_ID = re.compile(r"[?&]list=([^&]+)")


def fetch_metadata_many(urls, session=None):
    """Metadata for many URLs at once. YouTube ids are **batched**
    (``videos.list``, 50/call — keeps a paste-many or playlist import to a
    handful of API calls); Vimeo is per-URL oEmbed. One bad URL never sinks the
    batch: returns ``{url: {"ok": True, "metadata": {...}}}`` or
    ``{url: {"ok": False, "error": "..."}}`` per input URL."""
    session = session or requests.Session()
    results = {}
    youtube = {}  # yid -> [original urls]

    for raw in urls:
        url = (raw or "").strip()
        if not url:
            continue
        yid = durations.youtube_id(url)
        if yid:
            youtube.setdefault(yid, []).append(url)
        elif "vimeo.com" in url:
            try:
                results[url] = {"ok": True, "metadata": _fetch_vimeo(url, session)}
            except MetadataError as exc:
                results[url] = {"ok": False, "error": str(exc)}
        else:
            results[url] = {"ok": False, "error": "Not a YouTube or Vimeo link."}

    ids = list(youtube)
    for start in range(0, len(ids), YT_BATCH):
        _resolve_youtube_batch(ids[start : start + YT_BATCH], youtube, session, results)
    return results


def _resolve_youtube_batch(batch, youtube, session, results):
    """Look up one batch of YouTube ids and record a result for every URL that
    mapped to them (into ``results``, keyed by original URL)."""
    try:
        data = youtube_live.api_get(session, "videos", part="snippet,contentDetails", id=",".join(batch))
        found = {item["id"]: item for item in data.get("items", [])}
    except (youtube_live.YoutubeApiError, KeyError):
        found = None
    for yid in batch:
        if found is None:
            outcome = {"ok": False, "error": "Couldn't reach YouTube just now."}
        elif yid not in found:
            outcome = {"ok": False, "error": "Video not found (private or deleted)."}
        else:
            outcome = {"ok": True, "metadata": _youtube_doc(yid, found[yid])}
        for url in youtube[yid]:
            results[url] = outcome


def youtube_playlist_video_urls(playlist_url, session=None, max_items=200):
    """Expand a YouTube playlist URL to its video watch-URLs (``playlistItems``,
    paginated 50/page, capped at ``max_items``). Raises ``MetadataError`` for a
    non-playlist link or an empty/private playlist."""
    match = _PLAYLIST_ID.search(playlist_url or "")
    if not match:
        raise MetadataError("That doesn't look like a YouTube playlist link.")
    playlist_id = match.group(1)
    session = session or requests.Session()

    urls = []
    page_token = None
    while len(urls) < max_items:
        params = {"part": "contentDetails", "maxResults": YT_BATCH, "playlistId": playlist_id}
        if page_token:
            params["pageToken"] = page_token
        try:
            data = youtube_live.api_get(session, "playlistItems", **params)
        except (youtube_live.YoutubeApiError, KeyError) as exc:
            raise MetadataError("Couldn't load that playlist (it may be private).") from exc
        for item in data.get("items", []):
            vid = item.get("contentDetails", {}).get("videoId")
            if vid:
                urls.append(f"https://www.youtube.com/watch?v={vid}")
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    if not urls:
        raise MetadataError("That playlist has no videos (or is private).")
    return urls[:max_items]
