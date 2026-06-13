"""Strict Inertia prop encoder — fail loud on raw Django models.

inertia-django's default encoder expands a `Model` prop via `model_to_dict`,
which follows the model's relations. Our catalogue data is cyclic
(Video → series → demographic → video → …), so that recurses until the worker
crashes — a silent, catastrophic 500 (Sentry CLAYTONTV-6).

Props must be plain JSON-able data: build them explicitly (e.g.
`app.cards.video_card_props`). This encoder turns an *accidental* model/queryset
prop into an immediate, descriptive error instead of an infinite loop, so a
regression is caught by that view's feature test (and in CI) rather than in
production. Escape hatch preserved: a model that declares `InertiaMeta.fields`
still serializes safely via the parent encoder.
"""

from django.db import models
from django.db.models.query import QuerySet
from inertia.utils import InertiaJsonEncoder

_HINT = "Build a plain dict/list of the fields the page needs (e.g. video_card_props(...))"


class StrictInertiaJsonEncoder(InertiaJsonEncoder):
    def default(self, value):
        if isinstance(value, (models.Manager, QuerySet)):
            raise TypeError(
                f"Refusing to serialize a {type(value).__name__} as an Inertia prop. {_HINT} — "
                "passing the queryset serializes each model's relations and recurses on cyclic data."
            )
        if isinstance(value, models.Model) and not hasattr(type(value), "InertiaMeta"):
            raise TypeError(
                f"Refusing to serialize the {type(value).__name__} model as an Inertia prop. {_HINT}, "
                "or declare an InertiaMeta on the model — never pass the bare model, whose relations "
                "recurse and crash serialization."
            )
        return super().default(value)
