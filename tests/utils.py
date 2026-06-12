import json
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
