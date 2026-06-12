"""Idempotent ingestion from the legacy programme dump (programmes.json).

Replaces the ClayScraper → ctvDBreform → CSV → delete-all-import chain.
Reads the dump directly so nothing is dropped in transit: all media URLs
(the old chain kept media[0] only), transcript/audio links, and label IDs.

Every write is an upsert keyed on the legacy programme id — running twice
produces an identical database (proven in tests/test_ingest_legacy.py).
"""

from datetime import datetime

from django.db.models import Q

from catalogue.models import Bible_Book, RelatedResource, Speaker, Topic, Video

from .normalize import clean_name, clean_topic_name, detect_platform


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def video_media(programme):
    """The playable media entries, adverts excluded, in dump order."""
    return [m for m in programme.get("media", []) if m.get("type") == "Video" and m.get("url")]


def ingest_programme(programme, stats):
    """Upsert one programme and its links. Returns the Video or None if the
    programme has nothing playable (matches the old importer's skip rule)."""
    media = video_media(programme)
    if not media:
        stats["skipped_no_media"] += 1
        return None

    primary, *rest = media

    # url and id_number are unique, but the legacy dump contains duplicate
    # programme listings sharing both (37 duplicate refs found in recon).
    # Keep the first, report the rest for dedup review — never crash
    # mid-ingest, never silently swallow.
    ref = clean_name(programme.get("ref"))
    collision = Video.objects.filter(Q(url=primary["url"]) | Q(id_number=ref)).exclude(id=str(programme["id"])).first()
    if collision is not None:
        stats["skipped_url_collision"] += 1
        stats["url_collisions"].append({"programme_id": programme["id"], "kept_video_id": collision.id})
        return None
    fields = {
        "id_number": clean_name(programme.get("ref")),
        "name": clean_name(programme.get("name")),
        "description": programme.get("description") or "",
        "url": primary["url"],
        "alternate_urls": [{"url": m["url"], "platform": detect_platform(m["url"])} for m in rest],
        "thumbnail": programme.get("image") or primary.get("image"),
        # is_livestream is deliberately NOT set here: the authoritative signal
        # is membership in the legacy "BROWSE: LIVE STREAMS" series, which
        # series.json ingestion (session 2.2) will own. Name matching
        # undercounts badly (110 vs 654); until 2.2, the
        # backfill_livestream_flags reconciler remains the source of truth.
        "date_recorded": parse_date(programme.get("date_added")),
        "date_created": parse_date(programme.get("date_added")) or datetime.now().date(),
        "date_modified": parse_date(programme.get("date_modified")),
    }

    video, created = Video.objects.update_or_create(id=str(programme["id"]), defaults=fields)
    stats["created" if created else "updated"] += 1

    link_labels(video, programme)
    link_resources(video, programme)
    return video


def link_labels(video, programme):
    """Labels arrive with legacy IDs — link by ID, creating missing entries
    with normalized names. label_c ids are the canonical book order (1-66)."""
    speakers = []
    for label in programme.get("label_a") or []:
        speaker, _ = Speaker.objects.update_or_create(
            id=str(label["id"]),
            defaults={"name": clean_name(label.get("name")), "bio": "", "thumbnail": ""},
        )
        speakers.append(speaker)
    video.speaker.set(speakers)

    topics = []
    for label in programme.get("label_b") or []:
        name = clean_topic_name(label.get("name"))
        topic = Topic.objects.filter(id=str(label["id"])).first()
        if topic is None:
            topic, _ = Topic.objects.get_or_create(name=name, defaults={"id": str(label["id"]), "category": ""})
        topics.append(topic)
    video.topic.set(topics)

    books = []
    for label in programme.get("label_c") or []:
        book = Bible_Book.objects.filter(order=str(label["id"])).first()
        if book:
            books.append(book)
    video.bible_book.set(books)


def link_resources(video, programme):
    """Transcript/audio reference links, kept in sync with the dump."""
    wanted = set()
    for kind, key in (("transcript", "transcript_link"), ("audio", "audio_link")):
        url = (programme.get(key) or "").strip()
        if url.startswith("http") and len(url) <= 500:
            wanted.add((kind, url))
            RelatedResource.objects.get_or_create(video=video, kind=kind, url=url)
    video.related_resources.exclude(
        id__in=[r.id for r in video.related_resources.all() if (r.kind, r.url) in wanted]
    ).delete()


def ingest_programmes(programmes):
    stats = {"created": 0, "updated": 0, "skipped_no_media": 0, "skipped_url_collision": 0, "url_collisions": []}
    for programme in programmes:
        ingest_programme(programme, stats)
    return stats
