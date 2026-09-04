"""catalogue/metadata.py — the paste-a-URL metadata fetch behind the Studio's
Add-a-video form (Epic 3, Slice 3).

Network is faked: a YouTube videos.list payload and a Vimeo oEmbed payload are
fed through a stub session so we test our normalisation, not the platforms.
"""

import pytest

from catalogue.metadata import MetadataError, fetch_metadata


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._payload


class FakeSession:
    """Returns one canned response for every .get (enough for these single-call
    fetches), recording the calls for assertion."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self._status = status_code
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        return FakeResponse(self._payload, self._status)


YT_PAYLOAD = {
    "items": [
        {
            "snippet": {
                "title": "Sermon on the Mount",
                "description": "A talk about the Beatitudes.",
                "publishedAt": "2024-03-02T10:00:00Z",
                "thumbnails": {
                    "high": {"url": "https://img/high.jpg"},
                    "maxres": {"url": "https://img/maxres.jpg"},
                },
            },
            "contentDetails": {"duration": "PT28M50S"},
        }
    ]
}

VIMEO_PAYLOAD = {
    "video_id": 97249023,
    "title": "Cloning Humans",
    "description": "A documentary.",
    "thumbnail_url": "https://i.vimeocdn.com/x.jpg",
    "duration": 3600,
    "upload_date": "2014-05-30 12:00:00",
}


def test_fetch_youtube_metadata(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")  # gitleaks:allow
    session = FakeSession(YT_PAYLOAD)

    meta = fetch_metadata("https://www.youtube.com/watch?v=abc123XYZ_-", session=session)

    assert meta["platform"] == "youtube"
    assert meta["platform_id"] == "abc123XYZ_-"
    assert meta["url"] == "https://www.youtube.com/watch?v=abc123XYZ_-"
    assert meta["name"] == "Sermon on the Mount"
    assert meta["description"] == "A talk about the Beatitudes."
    assert meta["duration_seconds"] == 28 * 60 + 50
    assert meta["thumbnail"] == "https://img/maxres.jpg"  # highest resolution wins
    assert meta["date_recorded"] == "2024-03-02"


def test_fetch_youtube_not_found(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")  # gitleaks:allow
    with pytest.raises(MetadataError):
        fetch_metadata("https://youtu.be/missing12345", session=FakeSession({"items": []}))


def test_fetch_vimeo_metadata():
    session = FakeSession(VIMEO_PAYLOAD)

    meta = fetch_metadata("https://vimeo.com/97249023", session=session)

    assert meta["platform"] == "vimeo"
    assert meta["platform_id"] == "97249023"
    assert meta["url"] == "https://vimeo.com/97249023"
    assert meta["name"] == "Cloning Humans"
    assert meta["duration_seconds"] == 3600
    assert meta["thumbnail"] == "https://i.vimeocdn.com/x.jpg"
    assert meta["date_recorded"] == "2014-05-30"
    # The oEmbed endpoint was called with the pasted URL.
    assert session.calls and session.calls[0][1] == {"url": "https://vimeo.com/97249023"}


def test_fetch_vimeo_not_found():
    with pytest.raises(MetadataError):
        fetch_metadata("https://vimeo.com/000", session=FakeSession({}, status_code=404))


def test_unsupported_url_raises():
    with pytest.raises(MetadataError):
        fetch_metadata("https://example.com/not-a-video")


def test_empty_url_raises():
    with pytest.raises(MetadataError):
        fetch_metadata("")
