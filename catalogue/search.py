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

import typesense
from django.conf import settings

logger = logging.getLogger(__name__)

COLLECTION = "content"

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


def iter_content_docs():
    """Yield a Typesense doc for every searchable object. Counts mirror the view
    queries exactly so the proxy returns identical numbers."""
    from django.db.models import Count

    from catalogue.ingest.normalize import clean_name, clean_topic_name
    from catalogue.models.bible_book import Bible_Book
    from catalogue.models.channel import Channel
    from catalogue.models.demograpic import Demographic
    from catalogue.models.ministry import Ministry
    from catalogue.models.series import Series
    from catalogue.models.speaker import Speaker
    from catalogue.models.topic import Topic
    from catalogue.models.video import Video

    for v in Video.objects.all().iterator():
        yield build_video_doc(v)

    # Series videos live on the Series.videos M2M (the FK reverse is never set).
    for s in Series.objects.annotate(n=Count("videos")).iterator():
        yield build_category_doc(
            kind=KIND_SERIES,
            pk=s.pk,
            name=clean_name(s.name),
            text=s.summary or "",
            url=s.get_absolute_url(),
            videos_count=s.n,
        )

    for sp in Speaker.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_SPEAKER,
            pk=sp.pk,
            name=clean_name(sp.name),
            text=sp.bio or "",
            url=sp.get_absolute_url(),
            videos_count=sp.n,
        )

    for t in Topic.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_TOPIC,
            pk=t.pk,
            name=clean_topic_name(t.name),
            text=t.summary or "",
            url=t.get_absolute_url(),
            videos_count=t.n,
        )

    # Bible books: the display name lives behind a choice code; index that.
    for b in Bible_Book.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_BOOK,
            pk=b.pk,
            name=b.get_name_display(),
            text=b.summary or "",
            url=b.get_absolute_url(),
            videos_count=b.n,
        )

    for c in Channel.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_CHANNEL,
            pk=c.pk,
            name=clean_name(c.name),
            text=c.summary or "",
            url=c.get_absolute_url(),
            videos_count=c.n,
        )

    for m in Ministry.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_MINISTRY,
            pk=m.pk,
            name=clean_name(m.name),
            text=m.summary or "",
            url=m.get_absolute_url(),
            videos_count=m.n,
        )

    for a in Demographic.objects.annotate(n=Count("video")).iterator():
        yield build_category_doc(
            kind=KIND_AUDIENCE,
            pk=a.pk,
            name=clean_name(a.name),
            text=a.summary or "",
            url=a.get_absolute_url(),
            videos_count=a.n,
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


def search_videos(query, *, page=1, per_page=24):
    """Ranked video hits for ``query``. Returns ``(hits, found)``."""
    client = _require_client()
    try:
        res = client.collections[COLLECTION].documents.search(
            {
                "q": query,
                "query_by": QUERY_BY,
                "query_by_weights": QUERY_BY_WEIGHTS,
                "filter_by": f"kind:={KIND_VIDEO}",
                "page": page,
                "per_page": per_page,
                "sort_by": "_text_match:desc,date_epoch:desc",
                "include_fields": "pk,name,url,date_display,is_livestream,kind,videos_count",
            }
        )
    except typesense.exceptions.TypesenseClientError as e:
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
    except typesense.exceptions.TypesenseClientError as e:
        raise SearchUnavailableError(str(e)) from e
    hits = []
    for group in res.get("grouped_hits", []):
        hits.extend(_hit(h["document"]) for h in group.get("hits", []))
    return hits
