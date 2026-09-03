"""Fetch video thumbnails from Vimeo using their oEmbed API"""

import requests

from catalogue.models import Video

VIMEO_OEMBED = "https://vimeo.com/api/oembed.json"


def fetch_and_store_thumbnail_url(video, session=None):
    if "vimeo.com" not in (video.url or ""):
        return None
    session = session or requests.Session()
    response = session.get(VIMEO_OEMBED, params={"url": video.url}, timeout=15)
    thumbnail_url = response.json().get("thumbnail_url") if response.status_code == 200 else None
    if thumbnail_url:
        Video.objects.filter(id=video.id).update(thumbnail=thumbnail_url)
        return thumbnail_url
    else:
        return None
