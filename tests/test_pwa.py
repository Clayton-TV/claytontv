"""Phase 7 — app-feel & PWA guardrails.

The hard accessibility rule: pinch-zoom must stay enabled (elderly users rely
on it), so input-zoom is prevented via 16px font sizing in the design system,
never via user-scalable=no / maximum-scale.
"""

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db

MANIFEST = Path(__file__).resolve().parent.parent / "public" / "manifest.webmanifest"


def head_html(client):
    """The full first-load document (app.html), not an Inertia partial."""
    return client.get("/").content.decode()


def test_viewport_keeps_pinch_zoom_enabled(client):
    html = head_html(client)
    assert "width=device-width" in html
    # Elderly users rely on pinch-zoom — these must never appear.
    assert "user-scalable=no" not in html
    assert "maximum-scale" not in html


def test_viewport_opts_into_safe_area_insets(client):
    # viewport-fit=cover is what makes env(safe-area-inset-*) non-zero.
    assert "viewport-fit=cover" in head_html(client)


def test_pwa_head_links_manifest_and_chrome(client):
    html = head_html(client)
    assert 'rel="manifest"' in html
    assert 'name="theme-color"' in html
    assert 'name="apple-mobile-web-app-capable"' in html


def test_manifest_is_valid_and_installable():
    data = json.loads(MANIFEST.read_text())
    assert data["name"]
    assert data["short_name"]
    assert data["start_url"] == "/"
    assert data["display"] == "standalone"
    assert data["icons"], "needs at least one icon"
    assert any("maskable" in icon.get("purpose", "") for icon in data["icons"])
