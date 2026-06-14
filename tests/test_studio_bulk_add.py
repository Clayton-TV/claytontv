"""Studio bulk add (Epic 3, Slice 5): paste-many URLs + YouTube playlist import.

The metadata batch + playlist expansion are unit-tested against a stub session;
the service and endpoint are tested with the fetch layer patched so one bad URL
never sinks the batch and dedup/tallies are correct.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import catalogue.metadata as metadata
from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.metadata import MetadataError, fetch_metadata_many, youtube_playlist_video_urls
from catalogue.models.video import DRAFT, Video
from tests.factories import VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db

User = get_user_model()
PASSWORD = "pw-correct-horse-1"  # gitleaks:allow


def make_editor(username="editor"):
    user = User.objects.create_user(username=username, password=PASSWORD)
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    return user


def login_editor(client, username="editor"):
    make_editor(username)
    client.login(username=username, password=PASSWORD)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._payload


class DispatchSession:
    """Returns canned payloads keyed by which endpoint is hit."""

    def __init__(self, *, videos=None, oembed=None, playlist=None):
        self._videos = videos or {"items": []}
        self._oembed = oembed
        self._playlist = playlist or {"items": []}

    def get(self, url, params=None, timeout=None):
        if "oembed" in url:
            return FakeResponse(self._oembed or {}, 200 if self._oembed else 404)
        if "playlistItems" in url:
            return FakeResponse(self._playlist)
        return FakeResponse(self._videos)  # videos.list


# --- metadata batch -------------------------------------------------------


def test_fetch_metadata_many_batches_youtube_and_handles_mixed(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")  # gitleaks:allow
    videos_payload = {
        "items": [
            {
                "id": "aaaaaaaaaaa",
                "snippet": {"title": "First", "thumbnails": {}},
                "contentDetails": {"duration": "PT5M"},
            },
            {
                "id": "bbbbbbbbbbb",
                "snippet": {"title": "Second", "thumbnails": {}},
                "contentDetails": {"duration": "PT6M"},
            },
        ]
    }
    session = DispatchSession(videos=videos_payload)
    out = fetch_metadata_many(
        [
            "https://www.youtube.com/watch?v=aaaaaaaaaaa",
            "https://www.youtube.com/watch?v=bbbbbbbbbbb",
            "https://example.com/nope",
        ],
        session=session,
    )
    assert out["https://www.youtube.com/watch?v=aaaaaaaaaaa"]["metadata"]["name"] == "First"
    assert out["https://www.youtube.com/watch?v=bbbbbbbbbbb"]["ok"] is True
    assert out["https://example.com/nope"]["ok"] is False


def test_fetch_metadata_many_reports_missing_youtube(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")  # gitleaks:allow
    session = DispatchSession(videos={"items": []})  # id not returned → gone
    out = fetch_metadata_many(["https://youtu.be/zzzzzzzzzzz"], session=session)
    assert out["https://youtu.be/zzzzzzzzzzz"]["ok"] is False


# --- playlist expansion ---------------------------------------------------


def test_youtube_playlist_video_urls(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")  # gitleaks:allow
    payload = {
        "items": [
            {"contentDetails": {"videoId": "vid1"}},
            {"contentDetails": {"videoId": "vid2"}},
        ]
    }
    session = DispatchSession(playlist=payload)
    urls = youtube_playlist_video_urls("https://www.youtube.com/playlist?list=PL123", session=session)
    assert urls == ["https://www.youtube.com/watch?v=vid1", "https://www.youtube.com/watch?v=vid2"]


def test_youtube_playlist_rejects_non_playlist():
    with pytest.raises(MetadataError):
        youtube_playlist_video_urls("https://www.youtube.com/watch?v=abc")


# --- bulk_create_from_urls ------------------------------------------------


def _patch_fetch(monkeypatch, mapping):
    monkeypatch.setattr(metadata, "fetch_metadata_many", lambda urls, session=None: mapping)


def _meta(url, name="A talk"):
    metadata_dict = {
        "url": url,
        "name": name,
        "description": "",
        "thumbnail": None,
        "duration_seconds": 60,
        "date_recorded": None,
    }
    return {"ok": True, "metadata": metadata_dict}


def test_bulk_create_creates_drafts_and_tallies(monkeypatch):
    existing = VideoFactory(name="Already", url="https://youtu.be/dup")
    mapping = {
        "https://youtu.be/new1": _meta("https://youtu.be/new1", "New one"),
        "https://youtu.be/dup": _meta("https://youtu.be/dup", "Dup"),
        "https://bad/x": {"ok": False, "error": "Not a video link."},
    }
    _patch_fetch(monkeypatch, mapping)

    summary = services.bulk_create_from_urls(list(mapping))
    assert summary["created"] == 1
    assert summary["duplicates"] == 1
    assert summary["errors"] == 1
    new = Video.objects.get(url="https://youtu.be/new1")
    assert new.status == DRAFT
    # The duplicate row was not re-created.
    assert Video.all_objects.filter(url="https://youtu.be/dup").count() == 1
    assert existing.id != new.id


def test_bulk_create_dedupes_input(monkeypatch):
    mapping = {"https://youtu.be/same": _meta("https://youtu.be/same")}
    _patch_fetch(monkeypatch, mapping)
    summary = services.bulk_create_from_urls(["https://youtu.be/same", "https://youtu.be/same", "  "])
    assert summary["created"] == 1
    assert len(summary["results"]) == 1


# --- endpoints ------------------------------------------------------------


def test_bulk_page_requires_editor(client):
    assert client.get("/studio/bulk").status_code == 302  # anon → login


def test_bulk_page_renders_for_editor(client):
    login_editor(client)
    page = inertia_page(client.get("/studio/bulk"))
    assert page["component"] == "Studio/BulkAdd"


def test_bulk_create_endpoint_requires_editor(client):
    assert client.post("/studio/api/bulk-create").status_code == 302


def test_bulk_create_endpoint_creates_drafts(client, monkeypatch):
    login_editor(client)
    _patch_fetch(monkeypatch, {"https://youtu.be/e1": _meta("https://youtu.be/e1", "Endpoint one")})
    resp = client.post(
        "/studio/api/bulk-create",
        data=json.dumps({"urls": ["https://youtu.be/e1"]}),
        content_type="application/json",
    )
    body = resp.json()
    assert body["ok"] is True
    assert body["created"] == 1
    assert Video.objects.filter(url="https://youtu.be/e1").exists()


def test_bulk_create_endpoint_accepts_newline_string(client, monkeypatch):
    login_editor(client)
    _patch_fetch(monkeypatch, {"https://youtu.be/line1": _meta("https://youtu.be/line1")})
    resp = client.post(
        "/studio/api/bulk-create",
        data=json.dumps({"urls": "https://youtu.be/line1\n\n"}),
        content_type="application/json",
    )
    assert resp.json()["created"] == 1


def test_bulk_create_endpoint_empty_is_friendly_error(client):
    login_editor(client)
    body = client.post(
        "/studio/api/bulk-create",
        data=json.dumps({"urls": []}),
        content_type="application/json",
    ).json()
    assert body["ok"] is False
    assert "at least one" in body["error"]


def test_bulk_create_endpoint_expands_playlist(client, monkeypatch):
    login_editor(client)
    monkeypatch.setattr(services, "expand_playlist", lambda url: ["https://youtu.be/p1"])
    _patch_fetch(monkeypatch, {"https://youtu.be/p1": _meta("https://youtu.be/p1", "From playlist")})
    body = client.post(
        "/studio/api/bulk-create",
        data=json.dumps({"playlist_url": "https://www.youtube.com/playlist?list=PLx"}),
        content_type="application/json",
    ).json()
    assert body["ok"] is True
    assert body["created"] == 1


def test_bulk_create_endpoint_playlist_error_is_friendly(client, monkeypatch):
    login_editor(client)

    def boom(url):
        raise MetadataError("That playlist has no videos (or is private).")

    monkeypatch.setattr(services, "expand_playlist", boom)
    body = client.post(
        "/studio/api/bulk-create",
        data=json.dumps({"playlist_url": "https://www.youtube.com/playlist?list=PLbad"}),
        content_type="application/json",
    ).json()
    assert body["ok"] is False
    assert "playlist" in body["error"].lower()
