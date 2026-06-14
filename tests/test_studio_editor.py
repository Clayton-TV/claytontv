"""Studio editor (Epic 3, Slice 4a): the full tabbed EditVideo screen.

Covers the prefilled edit props (incl. the Series.videos M2M and related
resources), and the update service/endpoint — scalars, add AND remove of M2Ms,
series re-pointing, alternate_urls + related_resources sync, URL-clash guard,
and status-neutrality (Save never changes publication state).
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.models.related_resource import RelatedResource
from catalogue.models.video import DRAFT, PUBLISHED, Video
from tests.factories import (
    BibleBookFactory,
    DemographicFactory,
    MinistryFactory,
    SeriesFactory,
    SpeakerFactory,
    TopicFactory,
    VideoFactory,
)
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


# --- get_video_for_edit / the edit page ----------------------------------


def test_edit_props_include_relations_and_series_via_m2m():
    speaker = SpeakerFactory()
    topic = TopicFactory()
    series = SeriesFactory()
    video = VideoFactory(status=DRAFT)
    video.speaker.add(speaker)
    video.topic.add(topic)
    series.videos.add(video)  # membership lives on Series.videos, not Video.series
    RelatedResource.objects.create(video=video, kind="transcript", url="https://x.test/t")

    props = services.get_video_for_edit(video.id)

    assert props["id"] == video.id
    assert props["speaker_ids"] == [str(speaker.id)]
    assert props["topic_ids"] == [str(topic.id)]
    assert props["series_id"] == str(series.pk)
    assert props["related_resources"] == [{"kind": "transcript", "url": "https://x.test/t"}]


def test_get_video_for_edit_missing_returns_none():
    assert services.get_video_for_edit("nope") is None


def test_edit_page_anonymous_redirected(client):
    video = VideoFactory()
    resp = client.get(f"/studio/videos/{video.id}/edit")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/studio/login")


def test_edit_page_non_editor_forbidden(client):
    video = VideoFactory()
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    assert client.get(f"/studio/videos/{video.id}/edit").status_code == 403


def test_edit_page_renders_for_editor(client):
    login_editor(client)
    video = VideoFactory(name="Editable")
    page = inertia_page(client.get(f"/studio/videos/{video.id}/edit"))
    assert page["component"] == "Studio/EditVideo"
    assert page["props"]["video"]["name"] == "Editable"
    assert "taxonomy" in page["props"]


def test_edit_page_404_for_missing(client):
    login_editor(client)
    assert client.get("/studio/videos/ghost/edit").status_code == 404


# --- update service -------------------------------------------------------


def test_update_changes_scalar_fields():
    video = VideoFactory(name="Old", description="old")
    ok = services.update_video(
        video.id,
        name="New title",
        description="New body",
        url=video.url,
        duration_seconds=123,
    )
    assert ok is True
    video.refresh_from_db()
    assert video.name == "New title"
    assert video.description == "New body"
    assert video.duration_seconds == 123


def test_update_adds_and_removes_m2m():
    keep = SpeakerFactory()
    drop = SpeakerFactory()
    add = TopicFactory()
    video = VideoFactory()
    video.speaker.add(keep, drop)

    services.update_video(
        video.id,
        name=video.name,
        url=video.url,
        speaker_ids=[str(keep.id)],  # drops `drop`
        topic_ids=[str(add.id)],  # adds a topic
    )
    assert set(video.speaker.values_list("id", flat=True)) == {keep.id}
    assert set(video.topic.values_list("id", flat=True)) == {add.id}


def test_update_repoints_series_via_m2m():
    old = SeriesFactory()
    new = SeriesFactory()
    video = VideoFactory()
    old.videos.add(video)

    services.update_video(video.id, name=video.name, url=video.url, series_id=new.pk)

    assert not old.videos.filter(id=video.id).exists()
    assert new.videos.filter(id=video.id).exists()
    assert video.series_id is None  # decoy FK never used


def test_update_clearing_series_removes_membership():
    series = SeriesFactory()
    video = VideoFactory()
    series.videos.add(video)
    services.update_video(video.id, name=video.name, url=video.url, series_id=None)
    assert not series.videos.filter(id=video.id).exists()


def test_update_syncs_related_resources():
    video = VideoFactory()
    RelatedResource.objects.create(video=video, kind="audio", url="https://x.test/old")
    services.update_video(
        video.id,
        name=video.name,
        url=video.url,
        related_resources=[{"kind": "transcript", "url": "https://x.test/new"}],
    )
    rows = {(r.kind, r.url) for r in video.related_resources.all()}
    assert rows == {("transcript", "https://x.test/new")}


def test_update_replaces_alternate_urls():
    video = VideoFactory()
    alts = [{"url": "https://vimeo.com/1", "platform": "vimeo"}]
    services.update_video(video.id, name=video.name, url=video.url, alternate_urls=alts)
    video.refresh_from_db()
    assert video.alternate_urls == alts


def test_update_is_status_neutral():
    video = VideoFactory(status=PUBLISHED)
    services.update_video(video.id, name="changed", url=video.url)
    video.refresh_from_db()
    assert video.status == PUBLISHED  # Save never flips publication state


def test_update_missing_returns_false():
    assert services.update_video("ghost", name="x", url="https://x.test/y") is False


def test_update_url_clash_raises():
    other = VideoFactory(url="https://youtu.be/taken")
    video = VideoFactory()
    with pytest.raises(services.DuplicateVideoError):
        services.update_video(video.id, name=video.name, url="https://youtu.be/taken")
    # nothing changed
    assert Video.objects.get(id=other.id).url == "https://youtu.be/taken"


# --- update endpoint ------------------------------------------------------


def test_update_endpoint_requires_editor(client):
    video = VideoFactory()
    assert client.post(f"/studio/videos/{video.id}/update").status_code == 302  # anon → login


def test_update_endpoint_saves_via_json_body(client):
    login_editor(client)
    speaker = SpeakerFactory()
    book = BibleBookFactory(name="EXO")
    demo = DemographicFactory()
    ministry = MinistryFactory()
    video = VideoFactory(name="Before")

    resp = client.post(
        f"/studio/videos/{video.id}/update",
        data=json.dumps(
            {
                "name": "After",
                "url": video.url,
                "description": "Edited.",
                "speaker_ids": [str(speaker.id)],
                "bible_book_ids": [str(book.id)],
                "demographic_ids": [str(demo.id)],
                "ministry_ids": [str(ministry.id)],
                "related_resources": [{"kind": "other", "url": "https://x.test/r"}],
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/studio"
    video.refresh_from_db()
    assert video.name == "After"
    assert set(video.speaker.values_list("id", flat=True)) == {speaker.id}
    assert video.related_resources.count() == 1


def test_update_endpoint_url_clash_rerenders_with_error(client):
    login_editor(client)
    VideoFactory(name="Owner", url="https://youtu.be/owned")
    video = VideoFactory()
    resp = client.post(
        f"/studio/videos/{video.id}/update",
        data=json.dumps({"name": video.name, "url": "https://youtu.be/owned"}),
        content_type="application/json",
    )
    page = inertia_page(resp)
    assert page["component"] == "Studio/EditVideo"
    assert "url" in page["props"]["errors"]
