"""Issue #110: legacy descriptions ship raw HTML rendered via v-html — keep
the formatting, drop the breakage (invisible colour directives) and the XSS."""

import pytest

from app.sanitize import sanitize_description
from tests.factories import VideoFactory
from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("value", [None, "", "Just plain text, no tags."])
def test_passes_through_empty_and_plain(value):
    assert sanitize_description(value) == value


def test_keeps_allowlisted_formatting_tags():
    # bs4 may normalize void tags (<br> → <br/>); the tags themselves survive.
    cleaned = sanitize_description("<p>Welcome <strong>back</strong>.<br>New <em>series</em> below.</p>")
    for fragment in ("<p>", "<strong>back</strong>", "<br", "<em>series</em>"):
        assert fragment in cleaned


def test_strips_style_and_colour_directives_but_keeps_text():
    # The Gospel Choir May 2018 case: white-on-white text is invisible. We drop
    # the attributes (and unwrap the bare <font>/<span> wrappers) so the words
    # render in the page's own colour.
    html = '<p style="color:#ffffff">Praise <font color="white">team</font></p>'

    cleaned = sanitize_description(html)

    assert "style" not in cleaned
    assert "color" not in cleaned
    assert "<font" not in cleaned
    assert "Praise" in cleaned and "team" in cleaned


def test_removes_script_and_event_handlers():
    html = '<p onclick="steal()">Hi</p><script>alert(1)</script>'

    cleaned = sanitize_description(html)

    assert "script" not in cleaned.lower()
    assert "onclick" not in cleaned
    assert "Hi" in cleaned


def test_keeps_safe_links_drops_javascript_href():
    assert 'href="https://example.com"' in sanitize_description('<a href="https://example.com">x</a>')
    cleaned = sanitize_description('<a href="javascript:alert(1)">x</a>')
    assert "javascript" not in cleaned
    assert ">x</a>" in cleaned  # the link text survives, the href is gone


def test_watch_page_serves_sanitized_description(client):
    video = VideoFactory(description='<p style="color:#fff">Sunday <font color="white">service</font></p>')

    response = client.get(f"/video/{video.id}")

    description = inertia_page(response)["props"]["video"]["description"]
    assert "style" not in description
    assert "<font" not in description
    assert "Sunday" in description and "service" in description
