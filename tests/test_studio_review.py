"""Studio Review queue + soft-delete (Epic 3, Slice 4b).

Reject soft-deletes (Laravel-style ``deleted_at``): trashed videos vanish from
the Library, the public site and search, but are retained and restorable. The
default manager enforces this everywhere; ``Video.all_objects`` is the escape
hatch.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from app.auth import EDITORS_GROUP
from app.studio import services
from catalogue.models.video import DRAFT, PUBLISHED, Video
from tests.factories import SeriesFactory, VideoFactory
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


# --- soft delete ----------------------------------------------------------


def test_soft_delete_hides_from_default_manager_but_retains_row():
    video = VideoFactory()
    services.delete_videos([video.id])

    assert not Video.objects.filter(id=video.id).exists()  # hidden from default
    trashed = Video.all_objects.get(id=video.id)  # but retained
    assert trashed.deleted_at is not None


def test_soft_deleted_published_video_hidden_from_public_queries():
    video = VideoFactory(status=PUBLISHED)
    services.delete_videos([video.id])
    assert not Video.objects.published().filter(id=video.id).exists()


def test_soft_deleted_video_drops_out_of_series_relation():
    """The default-manager global scope must reach reverse relations too."""
    series = SeriesFactory()
    video = VideoFactory(status=PUBLISHED)
    series.videos.add(video)
    assert series.videos.filter(id=video.id).exists()

    services.delete_videos([video.id])
    assert not series.videos.filter(id=video.id).exists()


def test_create_against_trashed_url_is_duplicate_not_crash():
    """A trashed row still holds the unique URL, so a create must report a
    duplicate (via all_objects) rather than hit an IntegrityError."""
    gone = VideoFactory(url="https://youtu.be/trashed-url")
    services.delete_videos([gone.id])
    with pytest.raises(services.DuplicateVideoError):
        services.create_video(url="https://youtu.be/trashed-url", name="Retry")


def test_minted_id_skips_trashed_rows():
    a = services.create_video(url="https://youtu.be/mint-a", name="A")
    services.delete_videos([a.id])  # a is now trashed but still owns S0000001
    b = services.create_video(url="https://youtu.be/mint-b", name="B")
    assert b.id != a.id  # the minter counted the trashed row


def test_restore_brings_video_back():
    video = VideoFactory()
    services.delete_videos([video.id])
    assert not Video.objects.filter(id=video.id).exists()

    restored = services.restore_videos([video.id])
    assert restored == 1
    assert Video.objects.filter(id=video.id).exists()


def test_library_excludes_trashed():
    VideoFactory(name="Alive one")
    gone = VideoFactory(name="Trashed one")
    services.delete_videos([gone.id])
    names = {row["name"] for row in services.list_videos()["videos"]}
    assert names == {"Alive one"}


def test_draft_count_ignores_trashed():
    VideoFactory(status=DRAFT)
    gone = VideoFactory(status=DRAFT)
    services.delete_videos([gone.id])
    assert services.draft_count() == 1


# --- the review queue -----------------------------------------------------


def test_review_anonymous_redirected(client):
    resp = client.get("/studio/review")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/studio/login")


def test_review_non_editor_forbidden(client):
    User.objects.create_user(username="viewer", password=PASSWORD)
    client.login(username="viewer", password=PASSWORD)
    assert client.get("/studio/review").status_code == 403


def test_review_lists_drafts_only(client):
    login_editor(client)
    VideoFactory(name="A draft", status=DRAFT)
    VideoFactory(name="Live already", status=PUBLISHED)

    page = inertia_page(client.get("/studio/review"))
    assert page["component"] == "Studio/Review"
    names = {row["name"] for row in page["props"]["videos"]}
    assert names == {"A draft"}


def test_review_approve_publishes_via_status_endpoint(client):
    login_editor(client)
    draft = VideoFactory(status=DRAFT)
    resp = client.post(
        f"/studio/videos/{draft.id}/status",
        data=json.dumps({"status": PUBLISHED, "next": "/studio/review"}),
        content_type="application/json",
    )
    assert resp.status_code == 302
    draft.refresh_from_db()
    assert draft.status == PUBLISHED


def test_review_reject_soft_deletes_via_delete_endpoint(client):
    login_editor(client)
    draft = VideoFactory(status=DRAFT)
    resp = client.post(
        "/studio/videos/delete",
        data=json.dumps({"ids": [draft.id], "next": "/studio/review"}),
        content_type="application/json",
    )
    assert resp.status_code == 302
    assert not Video.objects.filter(id=draft.id).exists()  # gone from the queue
    assert Video.all_objects.get(id=draft.id).deleted_at is not None  # retained


def test_bulk_approve_publishes_selected(client):
    login_editor(client)
    a = VideoFactory(status=DRAFT)
    b = VideoFactory(status=DRAFT)
    resp = client.post(
        "/studio/videos/bulk-status",
        data=json.dumps({"status": PUBLISHED, "ids": [a.id, b.id], "next": "/studio/review"}),
        content_type="application/json",
    )
    assert resp.status_code == 302
    assert Video.objects.filter(status=PUBLISHED, id__in=[a.id, b.id]).count() == 2


def test_library_shows_review_draft_count(client):
    login_editor(client)
    VideoFactory(status=DRAFT)
    VideoFactory(status=DRAFT)
    VideoFactory(status=PUBLISHED)
    page = inertia_page(client.get("/studio/"))
    assert page["props"]["draft_count"] == 2
