from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def inertia_page_json(page: str) -> str:
    """Make the Inertia page JSON safe to embed in a <script type="application/json"> element.

    Script elements are raw text, so HTML entity escaping would corrupt the JSON.
    In valid JSON, "<", ">" and "&" can only occur inside string values, where the
    equivalent \\uXXXX escape is legal — replacing them prevents </script> breakout
    without changing what JSON.parse returns.
    """
    return mark_safe(page.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e"))
