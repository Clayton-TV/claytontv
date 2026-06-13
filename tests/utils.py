import json
import os
import re

PAGE_SCRIPT_RE = re.compile(
    rb'<script data-page="app" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def inertia_page(response):
    """Extract the Inertia page object (component, props, url...) from a first-load response."""
    match = PAGE_SCRIPT_RE.search(response.content)
    assert match, "Response contains no Inertia page payload"
    return json.loads(match.group(1))


def typesense_env_config():
    """Typesense settings from the environment, or ``None`` if no API key is set.

    test_settings disables Typesense so the suite is deterministic on the ORM
    fallback; the guarded live search tests use this to opt into a real server.
    """
    api_key = os.environ.get("TYPESENSE_API_KEY")
    if not api_key:
        return None
    return {
        "api_key": api_key,
        "host": os.environ.get("TYPESENSE_HOST", "127.0.0.1"),
        "port": os.environ.get("TYPESENSE_PORT", "8108"),
        "protocol": os.environ.get("TYPESENSE_PROTOCOL", "http"),
        "connection_timeout_seconds": 2,
    }
