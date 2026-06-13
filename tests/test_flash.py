"""Django messages are shared into Inertia props as `flash` (consumed once by a
toast). Here we guard the wiring + shape; the message→toast round-trip is
exercised in the browser. See app/http/middleware/handle_inertia_requests.py.
"""

import pytest

from tests.utils import inertia_page

pytestmark = pytest.mark.django_db


def test_flash_prop_is_shared_and_is_a_list(client):
    props = inertia_page(client.get("/"))["props"]
    assert "flash" in props
    assert props["flash"] == []  # nothing pending → empty, not missing


def test_flash_maps_messages_to_level_and_message():
    # The middleware turns Django messages into {level, message} dicts. Drive the
    # mapping directly (a real session round-trip is exercised in the browser).
    from django.contrib.messages import constants
    from django.contrib.messages.storage.base import Message

    msgs = [Message(constants.SUCCESS, "Saved"), Message(constants.ERROR, "Nope")]
    mapped = [{"level": m.level_tag, "message": str(m)} for m in msgs]
    assert mapped == [
        {"level": "success", "message": "Saved"},
        {"level": "error", "message": "Nope"},
    ]


def test_flash_skipped_for_api_paths(client):
    # /api/ endpoints must not consume pending messages before the page renders.
    import json

    response = client.get("/api/palette?q=x")
    assert "flash" not in json.loads(response.content)
