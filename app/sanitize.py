"""Sanitize the raw HTML that legacy video descriptions carry.

Descriptions were authored in the old admin's rich-text box, so they arrive as
HTML — mostly harmless `<p>`/`<br>` formatting, but also inline `style`/`color`
directives (e.g. the Gospel Choir May 2018 service sets white-on-white text,
issue #110) and, in principle, anything a future editor could paste. The watch
page renders this with `v-html`, so it has to be made safe and predictable
*before* it reaches the client.

Strategy: keep a small allowlist of formatting tags, drop everything else
(unwrapping the children so the text survives), and strip every attribute —
that removes the colour directives and any `on*`/`href="javascript:"` vector in
one move. BeautifulSoup is already a project dependency; bleach is not, so we
build the allowlist on bs4 rather than pull in another package.
"""

from bs4 import BeautifulSoup

# Inline + block formatting that legitimately appears in descriptions. Anything
# outside this set (script, style, span colour-wrappers, …) is unwrapped.
ALLOWED_TAGS = frozenset({"p", "br", "b", "strong", "i", "em", "u", "ul", "ol", "li", "a", "blockquote"})

# Attributes kept per tag. Links keep their href (validated below); everything
# else — notably `style` and `color` — is dropped, which is what un-breaks the
# invisible-text descriptions.
ALLOWED_ATTRS = {"a": frozenset({"href"})}

# href schemes we trust. Anything else (javascript:, data:, …) loses the href.
SAFE_URL_SCHEMES = frozenset({"http", "https", "mailto"})


def _href_is_safe(href):
    value = (href or "").strip().lower()
    if value.startswith("/") or value.startswith("#"):
        return True  # site-relative / in-page anchors
    scheme = value.split(":", 1)[0] if ":" in value else ""
    return scheme in SAFE_URL_SCHEMES


def sanitize_description(html):
    """Return `html` reduced to the formatting allowlist, attribute-stripped.

    `None`/empty input passes straight through so callers can stay terse.
    """
    if not html:
        return html

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()  # drop the tag, keep its text
            continue

        allowed = ALLOWED_ATTRS.get(tag.name, frozenset())
        for attr in list(tag.attrs):
            if attr not in allowed:
                del tag[attr]

        if tag.name == "a" and not _href_is_safe(tag.get("href")):
            del tag["href"]

    return str(soup)
