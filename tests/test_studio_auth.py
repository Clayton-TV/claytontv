"""Studio auth foundation (Epic 3, Slice 1): the access gate, the custom login,
and the create_editor command. See app/studio/ and app/auth.py."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from app.auth import EDITORS_GROUP, can_edit_content

pytestmark = pytest.mark.django_db

User = get_user_model()


def make_user(username="ed", password="pw-correct-horse-1", **kwargs):
    return User.objects.create_user(username=username, password=password, **kwargs)


def make_editor(username="editor", password="pw-correct-horse-1"):
    user = make_user(username=username, password=password)
    group, _ = Group.objects.get_or_create(name=EDITORS_GROUP)
    user.groups.add(group)
    return user


# --- the gate -------------------------------------------------------------


def test_anonymous_studio_redirects_to_login(client):
    response = client.get("/studio/")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/studio/login")
    # Bounce-back target is preserved.
    assert "next=%2Fstudio%2F" in response.headers["Location"]


def test_logged_in_non_editor_is_forbidden(client):
    make_user(username="viewer")
    client.login(username="viewer", password="pw-correct-horse-1")
    response = client.get("/studio/")
    assert response.status_code == 403


def test_editor_in_group_reaches_studio(client):
    make_editor(username="ed1")
    client.login(username="ed1", password="pw-correct-horse-1")
    response = client.get("/studio/")
    assert response.status_code == 200


def test_staff_reaches_studio(client):
    make_user(username="boss", is_staff=True)
    client.login(username="boss", password="pw-correct-horse-1")
    response = client.get("/studio/")
    assert response.status_code == 200


def test_can_edit_content_admits_staff_and_editors_only():
    assert can_edit_content(make_user(username="plain")) is False
    assert can_edit_content(make_user(username="adm", is_staff=True)) is True
    assert can_edit_content(make_editor(username="ed2")) is True


# --- the login ------------------------------------------------------------


def test_login_get_renders_page_and_sets_csrf_cookie(client):
    response = client.get("/studio/login")
    assert response.status_code == 200
    # ensure_csrf_cookie must set the cookie so Inertia's axios can echo it.
    assert "csrftoken" in response.cookies


def test_login_bad_credentials_rerenders_with_error_and_no_session(client):
    make_editor(username="ed3")
    response = client.post(
        "/studio/login",
        {"username": "ed3", "password": "wrong"},
    )
    # Re-renders the page (200), does not redirect, and shares an error.
    assert response.status_code == 200
    assert b"Studio/Login" in response.content
    assert b"username or password" in response.content
    assert "_auth_user_id" not in client.session


def test_login_good_credentials_authenticates_and_redirects_to_studio(client):
    make_editor(username="ed4")
    response = client.post(
        "/studio/login",
        {"username": "ed4", "password": "pw-correct-horse-1"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio"
    assert "_auth_user_id" in client.session


def test_login_honours_safe_next(client):
    make_editor(username="ed5")
    response = client.post(
        "/studio/login",
        {"username": "ed5", "password": "pw-correct-horse-1", "next": "/studio/add"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio/add"


def test_login_rejects_unsafe_next(client):
    make_editor(username="ed6")
    response = client.post(
        "/studio/login",
        {"username": "ed6", "password": "pw-correct-horse-1", "next": "https://evil.example/"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio"


def test_login_when_already_authenticated_redirects(client):
    make_editor(username="ed7")
    client.login(username="ed7", password="pw-correct-horse-1")
    response = client.get("/studio/login")
    assert response.status_code == 302
    assert response.headers["Location"] == "/studio"


# --- create_editor command ------------------------------------------------


def test_create_editor_creates_group_and_user(capsys):
    assert not Group.objects.filter(name=EDITORS_GROUP).exists()
    call_command("create_editor", "newed", "newed@example.com")

    group = Group.objects.get(name=EDITORS_GROUP)
    user = User.objects.get(username="newed")
    assert user.email == "newed@example.com"
    assert group in user.groups.all()
    # No --password → unusable password, with a hint to set one.
    assert not user.has_usable_password()
    assert "changepassword newed" in capsys.readouterr().out


def test_create_editor_is_idempotent():
    call_command("create_editor", "twice", "twice@example.com")
    call_command("create_editor", "twice", "twice@example.com")

    assert User.objects.filter(username="twice").count() == 1
    assert Group.objects.filter(name=EDITORS_GROUP).count() == 1
    user = User.objects.get(username="twice")
    assert user.groups.filter(name=EDITORS_GROUP).count() == 1


def test_create_editor_sets_password_when_given():
    call_command("create_editor", "withpw", "withpw@example.com", "--password", "s3cret-pw-xyz")
    user = User.objects.get(username="withpw")
    assert user.check_password("s3cret-pw-xyz")
