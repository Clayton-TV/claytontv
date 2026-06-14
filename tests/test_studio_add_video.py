"""Studio Add-a-video (Epic 3, Slice 3): the paste-a-URL intake.

Covers the service layer (create a draft with the *correct* relations, dedup,
id minting) and the views (the gated form page, the JSON metadata endpoint, and
the create handler).
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import app.studio.views as studio_views
from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.metadata import MetadataError
from catalogue.models.video import DRAFT, PUBLISHED, Video
from tests.factories import SeriesFactory, SpeakerFactory, TopicFactory, VideoFactory
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


# --- service: create_video ------------------------------------------------


def test_create_video_makes_draft_with_relations():
    speaker = SpeakerFactory()
    topic = TopicFactory()
    series = SeriesFactory()

    video = services.create_video(
        url="https://www.youtube.com/watch?v=NEW1",
        name="A fresh sermon",
        description="Notes.",
        duration_seconds=1730,
        status=DRAFT,
        speaker_ids=[speaker.id],
        topic_ids=[topic.id],
        series_id=series.pk,
    )

    assert video.status == DRAFT
    assert video.id.startswith("S")
    assert video.id_number == video.id
    assert list(video.speaker.all()) == [speaker]
    assert list(video.topic.all()) == [topic]
    # Series membership lives on Series.videos (M2M) — NOT the decoy Video.series FK.
    assert video.series_id is None
    assert series.videos.filter(id=video.id).exists()


def test_create_video_published_is_publicly_visible():
    video = services.create_video(
        url="https://www.youtube.com/watch?v=PUB1",
        name="Published one",
        status=PUBLISHED,
    )
    assert Video.objects.published().filter(id=video.id).exists()


def test_create_video_duplicate_url_raises():
    VideoFactory(url="https://www.youtube.com/watch?v=DUPE")
    with pytest.raises(services.DuplicateVideoError) as exc:
        services.create_video(url="https://www.youtube.com/watch?v=DUPE", name="Again")
    assert exc.value.video is not None


def test_minted_ids_are_unique():
    a = services.create_video(url="https://vimeo.com/1", name="A")
    b = services.create_video(url="https://vimeo.com/2", name="B")
    assert a.id != b.id
    assert a.id.startswith("S") and b.id.startswith("S")


def test_unknown_status_falls_back_to_draft():
    video = services.create_video(url="https://vimeo.com/9", name="X", status="nonsense")
    assert video.status == DRAFT


# --- service: find_duplicate + taxonomy_options ---------------------------


def test_find_duplicate_returns_existing_or_none():
    VideoFactory(id="42", name="Already here", url="https://vimeo.com/777")
    assert services.find_duplicate("https://vimeo.com/777") == {"id": "42", "name": "Already here"}
    assert services.find_duplicate("https://vimeo.com/absent") is None


def test_taxonomy_options_shape():
    SpeakerFactory(name="Zed Speaker")
    TopicFactory(name="Grace")
    options = services.taxonomy_options()
    assert set(options) == {"speakers", "series", "topics", "bible_books", "demographics", "ministries"}
    assert {"id", "name"} <= set(options["speakers"][0])


# --- views: the Add page --------------------------------------------------


def test_add_page_anonymous_redirected(client):
    resp = client.get("/studio/add")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/studio/login")


def test_add_page_non_editor_forbidden(client):
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    assert client.get("/studio/add").status_code == 403


def test_add_page_renders_for_editor(client):
    login_editor(client)
    page = inertia_page(client.get("/studio/add"))
    assert page["component"] == "Studio/AddVideo"
    assert "taxonomy" in page["props"]


# --- views: the metadata endpoint -----------------------------------------


def test_fetch_metadata_requires_editor(client):
    assert client.post("/studio/api/fetch-metadata").status_code == 302  # anon → login


def test_fetch_metadata_returns_preview(client, monkeypatch):
    login_editor(client)
    fake = {
        "platform": "youtube",
        "platform_id": "abc",
        "url": "https://www.youtube.com/watch?v=abc",
        "name": "Preview me",
        "description": "",
        "thumbnail": "https://img/x.jpg",
        "duration_seconds": 600,
        "date_recorded": "2024-01-01",
    }
    monkeypatch.setattr(studio_views, "fetch_metadata", lambda url: fake)

    resp = client.post(
        "/studio/api/fetch-metadata",
        data='{"url": "https://www.youtube.com/watch?v=abc"}',
        content_type="application/json",
    )
    body = resp.json()
    assert body["ok"] is True
    assert body["metadata"]["name"] == "Preview me"
    assert body["duplicate"] is None


def test_fetch_metadata_flags_duplicate(client, monkeypatch):
    login_editor(client)
    VideoFactory(id="99", name="Existing", url="https://www.youtube.com/watch?v=dup")
    fake = {"platform": "youtube", "url": "https://www.youtube.com/watch?v=dup", "name": "x"}
    monkeypatch.setattr(studio_views, "fetch_metadata", lambda url: fake)

    body = client.post(
        "/studio/api/fetch-metadata",
        data='{"url": "https://www.youtube.com/watch?v=dup"}',
        content_type="application/json",
    ).json()
    assert body["ok"] is True
    assert body["duplicate"] == {"id": "99", "name": "Existing"}


def test_fetch_metadata_reports_error(client, monkeypatch):
    login_editor(client)

    def boom(url):
        raise MetadataError("That doesn't look like a YouTube or Vimeo link.")

    monkeypatch.setattr(studio_views, "fetch_metadata", boom)
    body = client.post(
        "/studio/api/fetch-metadata",
        data='{"url": "https://example.com"}',
        content_type="application/json",
    ).json()
    assert body["ok"] is False
    assert "YouTube or Vimeo" in body["error"]


# --- views: the create handler --------------------------------------------


def test_create_endpoint_requires_editor(client):
    assert client.post("/studio/videos/create").status_code == 302  # anon → login


def test_create_endpoint_creates_draft_and_redirects(client):
    login_editor(client)
    speaker = SpeakerFactory()
    series = SeriesFactory()

    resp = client.post(
        "/studio/videos/create",
        {
            "url": "https://www.youtube.com/watch?v=CREATED",
            "name": "Created via form",
            "description": "Body.",
            "status": DRAFT,
            "speaker_ids": [speaker.id],
            "series_id": series.pk,
        },
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/studio"

    video = Video.objects.get(url="https://www.youtube.com/watch?v=CREATED")
    assert video.status == DRAFT
    assert list(video.speaker.all()) == [speaker]
    assert series.videos.filter(id=video.id).exists()


def test_create_endpoint_accepts_json_body(client):
    """Inertia posts a JSON body (not form-encoded), so the view must read it.
    Regression guard for the request.POST-is-empty trap."""
    login_editor(client)
    speaker = SpeakerFactory()
    resp = client.post(
        "/studio/videos/create",
        data=json.dumps(
            {
                "url": "https://www.youtube.com/watch?v=JSONBODY",
                "name": "Posted as JSON",
                "status": DRAFT,
                "speaker_ids": [speaker.id],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 302
    video = Video.objects.get(url="https://www.youtube.com/watch?v=JSONBODY")
    assert list(video.speaker.all()) == [speaker]


def test_create_endpoint_rejects_duplicate(client):
    login_editor(client)
    VideoFactory(name="The original", url="https://vimeo.com/dupe-create")

    resp = client.post(
        "/studio/videos/create",
        {"url": "https://vimeo.com/dupe-create", "name": "Trying again", "status": DRAFT},
    )
    # Re-renders the Add page with an inline error; no second row created.
    page = inertia_page(resp)
    assert page["component"] == "Studio/AddVideo"
    assert "url" in page["props"]["errors"]
    assert Video.objects.filter(url="https://vimeo.com/dupe-create").count() == 1
