"""VideoAdmin soft-delete visibility + restore/trash actions (#284).

Trashed videos must stay visible and recoverable in the Django admin — the
default manager hides them, so VideoAdmin uses ``all_objects`` and provides
restore/trash actions.
"""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from app.studio import services
from catalogue.admin import VideoAdmin
from catalogue.models.video import Video
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


def _request():
    request = RequestFactory().post("/admin/catalogue/video/")
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def test_admin_queryset_includes_trashed():
    video = VideoFactory()
    services.delete_videos([video.id])  # soft delete
    assert not Video.objects.filter(id=video.id).exists()  # hidden from default manager

    admin = VideoAdmin(Video, AdminSite())
    assert admin.get_queryset(_request()).filter(id=video.id).exists()  # visible in admin


def test_admin_restore_action_recovers_a_trashed_video():
    video = VideoFactory()
    services.delete_videos([video.id])

    admin = VideoAdmin(Video, AdminSite())
    admin.restore_selected(_request(), Video.all_objects.filter(id=video.id))

    assert Video.objects.filter(id=video.id).exists()  # back in the default manager


def test_admin_trash_action_soft_deletes():
    video = VideoFactory()
    admin = VideoAdmin(Video, AdminSite())
    admin.trash_selected(_request(), Video.all_objects.filter(id=video.id))

    assert not Video.objects.filter(id=video.id).exists()
    assert Video.all_objects.get(id=video.id).deleted_at is not None


def test_admin_changelist_renders_with_trash_filter(client, django_user_model):
    """The real admin ChangeList (custom filter + all_objects queryset) must
    render without error, and the Trashed filter must surface trashed rows."""
    django_user_model.objects.create_superuser("boss", "boss@example.com", "pw-xyz-1")  # gitleaks:allow
    client.login(username="boss", password="pw-xyz-1")  # gitleaks:allow
    VideoFactory(name="Live talk")
    gone = VideoFactory(name="Trashed talk")
    services.delete_videos([gone.id])

    all_rows = client.get("/admin/catalogue/video/")
    assert all_rows.status_code == 200
    assert b"Live talk" in all_rows.content and b"Trashed talk" in all_rows.content  # both shown by default

    trashed_only = client.get("/admin/catalogue/video/?trash=trashed")
    assert trashed_only.status_code == 200
    assert b"Trashed talk" in trashed_only.content
    assert b"Live talk" not in trashed_only.content
