"""On-brand error pages must be wired (named exactly 404.html/500.html/403.html
so Django's default handlers render them) — not the plain built-in fallback.
"""

import pytest

pytestmark = pytest.mark.django_db


def test_404_renders_branded_page(client):
    response = client.get("/this-route-does-not-exist/")
    assert response.status_code == 404
    body = response.content.decode()
    assert "Error 404" in body
    assert "We couldn't find that page" in body
    # On-brand + a11y: brand red, no zoom-blocking viewport.
    assert "#ef4444" in body
    assert "maximum-scale" not in body


def test_500_template_is_self_contained_and_on_brand():
    # The 500 path has no app context, so the template must be standalone (no
    # Vite/Inertia includes) — assert by rendering it directly.
    from django.template.loader import render_to_string

    body = render_to_string("500.html")
    assert "Something went wrong" in body
    assert "{% " not in body  # no unrendered template tags / no app.html extend
    assert "vite_asset" not in body  # no Vite/Inertia asset dependency
    assert "<script" not in body.lower()  # fully static — no JS
    assert "maximum-scale" not in body
