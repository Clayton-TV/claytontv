"""Keep the Typesense index live as the catalogue changes.

Wired in ``CatalogueConfig.ready()``. On every save of an indexed model we upsert
its doc; on delete we remove it. Everything is **best-effort** — the handlers
swallow errors and no-op when Typesense is unconfigured/unreachable, so a search
outage can never block a model save (the hourly admin sync, the admin UI, etc.).

Counts on *related* category docs (e.g. a series' video count when a video is
linked) are not updated here — those self-heal on the nightly reconcile
(`reindex_search`); the directly-saved object is always fresh.
"""

import logging

from django.db.models.signals import post_delete, post_save

from catalogue import search

logger = logging.getLogger(__name__)


def _index(instance):
    try:
        search.index_object(instance)
    except Exception:
        logger.warning("Typesense index_object raised for %r", instance, exc_info=True)


def _deindex(instance):
    kind = search.kind_for(type(instance))
    if kind is None:
        return
    try:
        search.delete_object(kind, instance.pk)
    except Exception:
        logger.warning("Typesense delete_object raised for %r", instance, exc_info=True)


def _on_save(sender, instance, **kwargs):
    _index(instance)


def _on_delete(sender, instance, **kwargs):
    _deindex(instance)


def connect():
    """Connect post_save/post_delete for every indexed model. Idempotent via
    dispatch_uid, so a double-import won't double-fire."""
    from catalogue.models.bible_book import Bible_Book
    from catalogue.models.channel import Channel
    from catalogue.models.demograpic import Demographic
    from catalogue.models.ministry import Ministry
    from catalogue.models.series import Series
    from catalogue.models.speaker import Speaker
    from catalogue.models.topic import Topic
    from catalogue.models.video import Video

    models = [Video, Series, Speaker, Topic, Bible_Book, Channel, Ministry, Demographic]
    for model in models:
        post_save.connect(_on_save, sender=model, dispatch_uid=f"typesense_index_{model.__name__}")
        post_delete.connect(_on_delete, sender=model, dispatch_uid=f"typesense_deindex_{model.__name__}")
