"""Typesense search backend for the catalogue.

A single unified ``content`` collection holds every searchable thing — videos
and the category models (series, speakers, topics, Bible books, channels,
ministries, audiences) — each tagged with a ``kind``. The search views
(``app/views.py``: ``palette``, ``search``) query this collection and **fall
back to ORM ``icontains``** when Typesense is unconfigured or unreachable, so
search never hard-fails.

Video counts are baked into each category doc at index time, using the *same*
relation the views count (Series via the ``Series.videos`` M2M, everything else
via the ``video`` reverse — the ``Video.series`` FK is a decoy that is never
populated). A search therefore returns ranked results *and* the per-category
video counts with zero per-hit ORM queries.
"""

import contextlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
import typesense
from django.conf import settings

logger = logging.getLogger(__name__)

COLLECTION = "content"

# What "Typesense is unavailable" looks like in practice: API-level errors AND the
# raw httpx transport errors the client re-raises on a real outage (connection
# refused, timeout) — those do NOT subclass TypesenseClientError. Catch both so an
# outage is a quiet fallback, not an unexpected error.
TYPESENSE_ERRORS = (typesense.exceptions.TypesenseClientError, httpx.HTTPError)

# Canonical kinds stored on every doc. The views map these to their own display
# labels ("Series", "Bible Book", …) — keep the index labels stable.
KIND_VIDEO = "video"
KIND_SERIES = "series"
KIND_SPEAKER = "speaker"
KIND_TOPIC = "topic"
KIND_BOOK = "book"
KIND_CHANNEL = "channel"
KIND_MINISTRY = "ministry"
KIND_AUDIENCE = "audience"

# Mirrors catalogue.models.video.PUBLISHED (kept as a local literal to avoid an
# import cycle); used to filter public video search to published docs.
PUBLISHED = "published"

# `name` carries more signal than the long description/bio/summary `text`.
QUERY_BY = "name,text"
QUERY_BY_WEIGHTS = "4,1"

CONTENT_SCHEMA = {
    "name": COLLECTION,
    "fields": [
        {"name": "kind", "type": "string", "facet": True},
        {"name": "pk", "type": "string", "index": False, "optional": True},
        {"name": "name", "type": "string"},
        {"name": "text", "type": "string"},
        {"name": "url", "type": "string", "index": False, "optional": True},
        {"name": "videos_count", "type": "int32"},
        {"name": "date_epoch", "type": "int64", "optional": True},
        {"name": "date_display", "type": "string", "index": False, "optional": True},
        {"name": "is_livestream", "type": "bool", "facet": True, "optional": True},
        # Videos carry their publication state; categories are always "published".
        # Public search filters status:=published; the Studio search omits it.
        {"name": "status", "type": "string", "facet": True, "optional": True},
    ],
    # Global tiebreaker: more-watched categories rank first when relevance ties.
    "default_sorting_field": "videos_count",
}

# Church-domain synonyms so a search for one term matches its siblings. Multi-way
# set: any term finds documents containing any other.
SYNONYMS = {
    "talk": ["talk", "sermon", "message", "address", "preaching"],
}


class SearchUnavailableError(Exception):
    """Typesense is unconfigured or unreachable. Callers catch this and fall
    back to the ORM query so search keeps working."""


def get_client():
    """Build a Typesense client from settings, or ``None`` when no API key is
    configured (the signal to use the ORM fallback)."""
    cfg = getattr(settings, "TYPESENSE", None) or {}
    if not cfg.get("api_key"):
        return None
    return typesense.Client(
        {
            "api_key": cfg["api_key"],
            "nodes": [{"host": cfg["host"], "port": str(cfg["port"]), "protocol": cfg["protocol"]}],
            "connection_timeout_seconds": cfg.get("connection_timeout_seconds", 2),
        }
    )


def _require_client():
    client = get_client()
    if client is None:
        raise SearchUnavailableError("Typesense is not configured")
    return client


# --------------------------------------------------------------------------- #
# Document builders
# --------------------------------------------------------------------------- #


def _epoch(d):
    """A timezone-stable UTC-midnight epoch for a ``date`` (or ``None``)."""
    if d is None:
        return None
    return int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp())


def build_video_doc(video):
    recorded = video.date_recorded or video.date_created
    return {
        "id": f"{KIND_VIDEO}:{video.pk}",
        "kind": KIND_VIDEO,
        "pk": str(video.pk),
        "name": video.name or "",
        "text": video.description or "",
        "url": f"/video/{video.pk}",
        "videos_count": 0,
        "date_epoch": _epoch(recorded),
        "date_display": recorded.isoformat() if recorded else None,
        "is_livestream": bool(video.is_livestream),
        "status": video.status,
    }


def build_category_doc(*, kind, pk, name, text, url, videos_count):
    return {
        "id": f"{kind}:{pk}",
        "kind": kind,
        "pk": str(pk),
        "name": name or "",
        "text": text or "",
        "url": url or "",
        "videos_count": int(videos_count or 0),
    }


def _category_specs():
    """Per-category-model indexing spec, the single source of truth for both the
    full reindex and single-object upserts. Each entry:
    ``model -> (kind, count_relation, name_fn, text_fn)``. ``count_relation`` is
    the relation the views Count — Series via the ``videos`` M2M (the FK reverse
    is never populated), everything else via the ``video`` reverse.
    """
    from catalogue.ingest.normalize import clean_name, clean_topic_name
    from catalogue.models.bible_book import Bible_Book
    from catalogue.models.channel import Channel
    from catalogue.models.demograpic import Demographic
    from catalogue.models.ministry import Ministry
    from catalogue.models.series import Series
    from catalogue.models.speaker import Speaker
    from catalogue.models.topic import Topic

    return {
        Series: (KIND_SERIES, "videos", lambda o: clean_name(o.name), lambda o: o.summary or ""),
        Speaker: (KIND_SPEAKER, "video", lambda o: clean_name(o.name), lambda o: o.bio or ""),
        Topic: (KIND_TOPIC, "video", lambda o: clean_topic_name(o.name), lambda o: o.summary or ""),
        Bible_Book: (KIND_BOOK, "video", lambda o: o.get_name_display(), lambda o: o.summary or ""),
        Channel: (KIND_CHANNEL, "video", lambda o: clean_name(o.name), lambda o: o.summary or ""),
        Ministry: (KIND_MINISTRY, "video", lambda o: clean_name(o.name), lambda o: o.summary or ""),
        Demographic: (KIND_AUDIENCE, "video", lambda o: clean_name(o.name), lambda o: o.summary or ""),
    }


def iter_content_docs():
    """Yield a Typesense doc for every searchable object. Videos are indexed
    regardless of status (each carries its `status`; public search filters to
    published, the Studio search doesn't); category `videos_count` counts only
    published videos so draft-only categories don't show publicly."""
    from catalogue.models.video import Video, published_count

    for v in Video.objects.all().iterator():
        yield build_video_doc(v)

    for model, (kind, relation, name_fn, text_fn) in _category_specs().items():
        for obj in model.objects.annotate(n=published_count(relation)).iterator():
            yield build_category_doc(
                kind=kind,
                pk=obj.pk,
                name=name_fn(obj),
                text=text_fn(obj),
                url=obj.get_absolute_url(),
                videos_count=obj.n,
            )


def kind_for(model):
    """The index ``kind`` for a model class, or ``None`` if it isn't indexed."""
    from catalogue.models.video import Video

    if model is Video:
        return KIND_VIDEO
    spec = _category_specs().get(model)
    return spec[0] if spec else None


def build_doc_for(obj):
    """Build the content doc for a single instance (video or category), or
    ``None`` if its model isn't indexed. Category counts are computed fresh."""
    from catalogue.models.video import Video, published_count

    if isinstance(obj, Video):
        return build_video_doc(obj)
    spec = _category_specs().get(type(obj))
    if spec is None:
        return None
    kind, relation, name_fn, text_fn = spec
    count = type(obj).objects.filter(pk=obj.pk).aggregate(n=published_count(relation))["n"] or 0
    return build_category_doc(
        kind=kind,
        pk=obj.pk,
        name=name_fn(obj),
        text=text_fn(obj),
        url=obj.get_absolute_url(),
        videos_count=count,
    )


# --------------------------------------------------------------------------- #
# Index lifecycle
# --------------------------------------------------------------------------- #


def recreate_collection(client):
    """Drop and recreate the ``content`` collection, then (re)apply synonyms."""
    with contextlib.suppress(typesense.exceptions.ObjectNotFound):
        client.collections[COLLECTION].delete()
    client.collections.create(CONTENT_SCHEMA)
    for name, terms in SYNONYMS.items():
        client.collections[COLLECTION].synonyms.upsert(name, {"synonyms": terms})


def _import_batch(client, batch):
    results = client.collections[COLLECTION].documents.import_(batch, {"action": "upsert"})
    failures = [r for r in results if isinstance(r, dict) and not r.get("success", True)]
    for f in failures:
        logger.warning("Typesense import failure: %s", f.get("error", f))
    return len(batch) - len(failures)


def reindex(*, batch_size=500, log=None):
    """Full rebuild of the search index from the database. Returns the number of
    documents successfully indexed."""
    log = log or (lambda *_: None)
    client = _require_client()
    recreate_collection(client)

    total, batch = 0, []
    for doc in iter_content_docs():
        batch.append(doc)
        if len(batch) >= batch_size:
            total += _import_batch(client, batch)
            log(f"  …{total} indexed")
            batch = []
    if batch:
        total += _import_batch(client, batch)
    return total


def index_object(obj):
    """Upsert one object's doc. Best-effort: returns ``False`` (never raises)
    when Typesense is unconfigured or unreachable, so the model save it's wired
    to via a signal can't be blocked by a search outage."""
    client = get_client()
    if client is None:
        return False
    doc = build_doc_for(obj)
    if doc is None:
        return False
    try:
        client.collections[COLLECTION].documents.upsert(doc)
    except TYPESENSE_ERRORS as exc:
        logger.warning("Typesense upsert failed for %s: %s", doc.get("id"), exc)
        return False
    return True


def delete_object(kind, pk):
    """Delete one object's doc. Best-effort (see :func:`index_object`); a missing
    doc counts as success."""
    client = get_client()
    if client is None:
        return False
    try:
        client.collections[COLLECTION].documents[f"{kind}:{pk}"].delete()
    except typesense.exceptions.ObjectNotFound:
        return True
    except TYPESENSE_ERRORS as exc:
        logger.warning("Typesense delete failed for %s:%s: %s", kind, pk, exc)
        return False
    return True


# --------------------------------------------------------------------------- #
# Query helpers (used by the view proxy; raise SearchUnavailableError on any
# Typesense error so the view can fall back to ORM)
# --------------------------------------------------------------------------- #


@dataclass
class Hit:
    kind: str
    pk: str
    name: str
    url: str
    videos_count: int
    date_display: str | None = None
    is_livestream: bool = False


def _hit(doc):
    return Hit(
        kind=doc.get("kind", ""),
        pk=doc.get("pk", ""),
        name=doc.get("name", ""),
        url=doc.get("url", ""),
        videos_count=doc.get("videos_count", 0),
        date_display=doc.get("date_display"),
        is_livestream=doc.get("is_livestream", False),
    )


def search_videos(query, *, page=1, per_page=24, published_only=True):
    """Ranked video hits for ``query``. Returns ``(hits, found)``. Public callers
    keep ``published_only`` (drafts hidden); the Studio passes False to see all."""
    client = _require_client()
    filter_by = f"kind:={KIND_VIDEO}"
    if published_only:
        filter_by += f" && status:={PUBLISHED}"
    try:
        res = client.collections[COLLECTION].documents.search(
            {
                "q": query,
                "query_by": QUERY_BY,
                "query_by_weights": QUERY_BY_WEIGHTS,
                "filter_by": filter_by,
                "page": page,
                "per_page": per_page,
                "sort_by": "_text_match:desc,date_epoch:desc",
                "include_fields": "pk,name,url,date_display,is_livestream,kind,videos_count",
            }
        )
    except TYPESENSE_ERRORS as e:
        raise SearchUnavailableError(str(e)) from e
    return [_hit(h["document"]) for h in res.get("hits", [])], res.get("found", 0)


def search_categories(query, *, kinds, per_kind=6):
    """Up to ``per_kind`` ranked hits per kind, across the requested ``kinds``."""
    client = _require_client()
    try:
        res = client.collections[COLLECTION].documents.search(
            {
                "q": query,
                "query_by": QUERY_BY,
                "query_by_weights": QUERY_BY_WEIGHTS,
                "filter_by": f"kind:[{','.join(kinds)}]",
                "group_by": "kind",
                "group_limit": per_kind,
                "per_page": 50,
                "sort_by": "_text_match:desc,videos_count:desc",
                "include_fields": "pk,name,url,kind,videos_count",
            }
        )
    except TYPESENSE_ERRORS as e:
        raise SearchUnavailableError(str(e)) from e
    hits = []
    for group in res.get("grouped_hits", []):
        hits.extend(_hit(h["document"]) for h in group.get("hits", []))
    return hits
