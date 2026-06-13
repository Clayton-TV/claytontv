"""Light mode (#30): the base template must honour the OS colour-scheme
preference before first paint, not force dark. The per-component token
migration is verified visually; this locks the no-force-dark regression."""

import pytest

pytestmark = pytest.mark.django_db


def head_html(client):
    return client.get("/").content.decode()


def test_first_paint_follows_system_preference(client):
    html = head_html(client)
    # The pre-paint script must read the real OS preference...
    assert "prefers-color-scheme: dark" in html
    # ...and must NOT hard-force dark (the old FIXME stop-gap).
    assert "const prefersDark = true" not in html


def test_default_appearance_is_system(client):
    # No stored choice → "system"; the script only adds .dark when the OS asks.
    html = head_html(client)
    assert "localStorage.getItem('appearance') || 'system'" in html
