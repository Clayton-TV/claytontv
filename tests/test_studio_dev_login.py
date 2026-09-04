"""The beta-only secret dev-login magic link (/studio/dev-login?key=...).

Off unless STUDIO_DEV_LOGIN_KEY is set; even then it 404s without the matching
key, and only signs in an actual editor. Never enabled in tests by default.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings

from app.auth import EDITORS_GROUP

pytestmark = pytest.mark.django_db

DEV_KEY = "test-magic-key-123"  # gitleaks:allow


def _make_editor(username="ed"):
    user = get_user_model().objects.create_user(username, f"{username}@example.com")
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    return user


def test_dev_login_404_when_key_not_configured(client):
    # Default (no STUDIO_DEV_LOGIN_KEY) → the endpoint doesn't exist.
    _make_editor("ed")
    assert client.get("/studio/dev-login", {"key": "anything"}).status_code == 404


@override_settings(STUDIO_DEV_LOGIN_KEY=DEV_KEY, STUDIO_DEV_LOGIN_USER="ed")
def test_dev_login_404_on_wrong_or_missing_key(client):
    _make_editor("ed")
    assert client.get("/studio/dev-login", {"key": "wrong"}).status_code == 404
    assert client.get("/studio/dev-login").status_code == 404
    assert "_auth_user_id" not in client.session


@override_settings(STUDIO_DEV_LOGIN_KEY=DEV_KEY, STUDIO_DEV_LOGIN_USER="ed")
def test_dev_login_signs_in_the_configured_editor(client):
    _make_editor("ed")
    resp = client.get("/studio/dev-login", {"key": DEV_KEY})
    assert resp.status_code == 302
    assert resp.url == "/studio"
    assert client.session.get("_auth_user_id")  # session is authenticated
    # And the now-authenticated session reaches the gated Studio.
    assert client.get("/studio/").status_code == 200


@override_settings(STUDIO_DEV_LOGIN_KEY=DEV_KEY, STUDIO_DEV_LOGIN_USER="notaneditor")
def test_dev_login_404_when_target_is_not_an_editor(client):
    get_user_model().objects.create_user("notaneditor", "n@example.com")  # no Editors group
    assert client.get("/studio/dev-login", {"key": DEV_KEY}).status_code == 404
    assert "_auth_user_id" not in client.session


@override_settings(STUDIO_DEV_LOGIN_KEY=DEV_KEY, STUDIO_DEV_LOGIN_USER="ghost")
def test_dev_login_404_when_target_user_missing(client):
    assert client.get("/studio/dev-login", {"key": DEV_KEY}).status_code == 404
