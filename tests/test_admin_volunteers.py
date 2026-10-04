"""Volunteer-facing guidance on the Django video add form (#353)."""

import pytest

from catalogue.admin import VideoAdmin
from catalogue.models import Video
from tests.factories import BibleBookFactory

pytestmark = pytest.mark.django_db


def test_video_add_form_guides_volunteers_and_shows_full_bible_book_names(client, django_user_model):
    django_user_model.objects.create_superuser("volunteer", "volunteer@example.com", "pw-xyz-1")  # gitleaks:allow
    client.login(username="volunteer", password="pw-xyz-1")  # gitleaks:allow
    BibleBookFactory(name="GEN", order="1", type="LAW")
    BibleBookFactory(name="MAT", order="40", type="GOS")

    response = client.get("/admin/catalogue/video/add/")

    assert response.status_code == 200
    assert b"Add the title, description, source link and existing reference." in response.content
    assert b"Choose all relevant Bible books and categories to help visitors browse." in response.content
    assert b">Genesis</option>" in response.content
    assert b">Matthew</option>" in response.content
    assert b">GEN</option>" not in response.content
    assert b">MAT</option>" not in response.content

    fieldsets = VideoAdmin(Video, None).get_fieldsets(response.wsgi_request)
    assert all("collapse" not in options.get("classes", ()) for _, options in fieldsets)
