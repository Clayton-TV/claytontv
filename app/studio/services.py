"""Studio service functions: the data layer behind the Library views.

House style: thin views call these; these talk to the models. Everything the
Library renders comes back as **plain dicts** (never Video models) so the strict
Inertia encoder is happy and we never accidentally serialise the five M2M
relations a Video drags along.

Unlike every public surface, the Studio sees **all** statuses — drafts and
published alike — so these queries use ``Video.objects`` unfiltered, NOT
``.published()``.
"""

import logging

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from catalogue import search as search_index
from catalogue.models.bible_book import Bible_Book
from catalogue.models.demograpic import Demographic
from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import DRAFT, PUBLISHED, Video

logger = logging.getLogger(__name__)

# The status filter values the Library accepts (mapped to a query filter below).
STATUS_ALL = "all"
STATUS_CHOICES = (STATUS_ALL, PUBLISHED, DRAFT)

DEFAULT_PER_PAGE = 24


def _series_name_by_video_id(video_ids):
    """Map ``video id -> series name`` via the ``Series.videos`` M2M.

    Series membership lives on that M2M, NOT the ``Video.series`` FK (a decoy
    that is never populated). One query for the whole page keeps this off the
    N+1 path. A video in more than one series takes the first by name — rare in
    the catalogue and good enough for a list cell.
    """
    pairs = Series.objects.filter(videos__id__in=list(video_ids)).order_by("name").values_list("videos__id", "name")
    mapping = {}
    for vid, series_name in pairs:
        mapping.setdefault(vid, series_name)
    return mapping


def _serialize(videos):
    """Turn an iterable of Video models into Library row dicts.

    Speakers are prefetched by the caller, so ``video.speaker.all()`` is free.
    Date is the recorded date, falling back to created, as ISO (or None).
    """
    video_ids = [v.id for v in videos]
    series_names = _series_name_by_video_id(video_ids)
    rows = []
    for v in videos:
        recorded = v.date_recorded or v.date_created
        rows.append(
            {
                "id": v.id,
                "name": v.name,
                "thumbnail": v.thumbnail,
                "speakers": [s.name for s in v.speaker.all()],
                "series": series_names.get(v.id),
                "date": recorded.isoformat() if recorded else None,
                "status": v.status,
                "duration_seconds": v.duration_seconds,
            }
        )
    return rows


def _search_ids(query):
    """Ranked video ids for ``query`` across ALL statuses.

    Prefer Typesense (``published_only=False`` so drafts are included) and fall
    back to an ORM ``name__icontains`` match when search is unavailable — the
    same try/except → SearchUnavailableError pattern the public view proxy uses.
    Returns ``(ids, ordered)`` where ``ordered`` is True when the ids already
    carry a relevance order to preserve.
    """
    try:
        hits, _ = search_index.search_videos(query, page=1, per_page=500, published_only=False)
        return [h.pk for h in hits], True
    except search_index.SearchUnavailableError as exc:
        logger.info("studio library: Typesense unavailable, ORM fallback (%s)", exc)
    except Exception:
        logger.warning("studio library: search proxy error, ORM fallback", exc_info=True)
    ids = list(Video.objects.filter(name__icontains=query).values_list("id", flat=True))
    return ids, False


def list_videos(*, search="", status=STATUS_ALL, page=1, per_page=DEFAULT_PER_PAGE):
    """The Studio video list: filtered, searched, paginated — as plain dicts.

    Returns a dict ready to spread into the Inertia props: ``videos`` (the row
    dicts), ``total`` (matching count), and the pagination flags.
    """
    search = (search or "").strip()
    status = status if status in STATUS_CHOICES else STATUS_ALL

    qs = Video.objects.all()
    if status != STATUS_ALL:
        qs = qs.filter(status=status)

    if search:
        ids, ordered = _search_ids(search)
        qs = qs.filter(id__in=ids)
        if ordered:
            # Preserve Typesense's relevance order across the (status-filtered) ids.
            position = {pk: i for i, pk in enumerate(ids)}
            objects = sorted(
                qs.prefetch_related("speaker"),
                key=lambda v: position.get(v.id, len(ids)),
            )
            return _paginate(objects, page, per_page)
    # Newest first for the unsearched / ORM-fallback list — the daily "what's
    # new to flip live" view reads best most-recent-first.
    qs = qs.prefetch_related("speaker").order_by("-date_created", "-id")
    return _paginate(qs, page, per_page)


def _paginate(objects, page, per_page):
    paginator = Paginator(objects, per_page)
    try:
        page_num = int(page)
    except (TypeError, ValueError):
        page_num = 1
    page_num = max(1, min(page_num, paginator.num_pages))
    paginated = paginator.page(page_num)
    return {
        "videos": _serialize(list(paginated.object_list)),
        "total": paginator.count,
        "page": page_num,
        "num_pages": paginator.num_pages,
        "has_prev_page": paginated.has_previous(),
        "has_next_page": paginated.has_next(),
    }


def set_video_status(video_id, status):
    """Set one video's publication status. Returns True if a row changed.

    Saving re-fires the search signal, so a publish/unpublish flip propagates to
    the index for free. ``status`` must be ``draft`` or ``published``.
    """
    if status not in (DRAFT, PUBLISHED):
        return False
    video = Video.objects.filter(id=video_id).first()
    if video is None:
        return False
    video.status = status
    video.save(update_fields=["status"])
    return True


def set_videos_status(video_ids, status):
    """Bulk publish/unpublish. Returns the number of videos updated.

    Saves each instance (rather than a single ``.update()``) so the per-object
    search signal fires and the index stays in sync.
    """
    if status not in (DRAFT, PUBLISHED):
        return 0
    updated = 0
    for video in Video.objects.filter(id__in=list(video_ids)):
        video.status = status
        video.save(update_fields=["status"])
        updated += 1
    return updated


def delete_videos(video_ids):
    """Delete the given videos. Returns the number removed. The post_delete
    search signal drops each from the index."""
    deleted = 0
    for video in Video.objects.filter(id__in=list(video_ids)):
        video.delete()
        deleted += 1
    return deleted


# --------------------------------------------------------------------------- #
# Add a video (paste-a-URL intake — Slice 3)
# --------------------------------------------------------------------------- #


class DuplicateVideoError(Exception):
    """The URL is already in the catalogue. Carries the existing row so the view
    can offer a friendly "already in library — open it" link."""

    def __init__(self, video):
        self.video = video
        super().__init__(f"Video already exists: {video.id}")


def find_duplicate(url):
    """The existing video at this exact URL as a ``{id, name}`` dict, or None.

    A light pre-check so the Add form can warn *before* the editor fills in
    classification. ``Video.url`` is unique, so this is the authoritative match;
    ``create_video`` re-checks at save time to close the race.
    """
    existing = Video.objects.filter(url=(url or "").strip()).only("id", "name").first()
    return {"id": existing.id, "name": existing.name} if existing else None


def taxonomy_options():
    """Every classification choice the Add form offers, as plain ``{id, name}``
    lists keyed by relation. Small enough (a few thousand rows total) to ship to
    the page once and filter client-side."""
    return {
        "speakers": _options(Speaker),
        "series": _options(Series),
        "topics": _options(Topic),
        "bible_books": _options(Bible_Book),
        "demographics": _options(Demographic),
        "ministries": _options(Ministry),
    }


def _options(model):
    return [{"id": str(pk), "name": name} for pk, name in model.objects.order_by("name").values_list("pk", "name")]


def create_video(
    *,
    url,
    name,
    description="",
    thumbnail=None,
    duration_seconds=None,
    date_recorded=None,
    status=DRAFT,
    speaker_ids=(),
    topic_ids=(),
    bible_book_ids=(),
    demographic_ids=(),
    ministry_ids=(),
    series_id=None,
):
    """Create a Studio video and link its classification. Returns the Video.

    Mirrors the legacy importer (``catalogue/ingest/legacy.py``): mint an ``id``
    + ``id_number``, create the row, then link relations via ``.set()`` — and
    crucially link series through ``Series.videos`` (the M2M), never the decoy
    ``Video.series`` FK. Raises ``DuplicateVideoError`` if the URL already
    exists. New content defaults to ``draft``; the post_save signal indexes it.
    """
    url = (url or "").strip()
    existing = Video.objects.filter(url=url).first()
    if existing is not None:
        raise DuplicateVideoError(existing)

    if status not in (DRAFT, PUBLISHED):
        status = DRAFT

    video_id = _mint_video_id()
    video = Video.objects.create(
        id=video_id,
        id_number=video_id,  # unique by construction; legacy uses the ref, we have none
        name=(name or "").strip()[:200] or "Untitled",
        description=description or "",
        url=url,
        thumbnail=thumbnail,
        duration_seconds=duration_seconds,
        date_recorded=date_recorded,
        date_created=timezone.now().date(),
        status=status,
    )

    _link_relations(
        video,
        speaker_ids=speaker_ids,
        topic_ids=topic_ids,
        bible_book_ids=bible_book_ids,
        demographic_ids=demographic_ids,
        ministry_ids=ministry_ids,
        series_id=series_id,
    )
    # M2M writes don't fire Video.post_save, so re-save once relations are linked
    # to (re)index a doc that actually reflects its speaker/series/topic facets.
    video.save()
    return video


def _mint_video_id():
    """A unique, non-colliding primary key for a Studio-created video.

    Legacy ids are bare numeric strings; ours are ``S`` + a zero-padded counter
    (``S0000001``) so they never clash with a legacy id — even one the dying
    live-admin feed imports later — and fit the 10-char ``id`` column.
    """
    n = Video.objects.filter(id__startswith="S").count() + 1
    while True:
        candidate = f"S{n:07d}"
        if not Video.objects.filter(Q(id=candidate) | Q(id_number=candidate)).exists():
            return candidate
        n += 1


def _link_relations(video, *, speaker_ids, topic_ids, bible_book_ids, demographic_ids, ministry_ids, series_id):
    """Wire the M2M classifications. Unknown ids are silently dropped (the form
    only ever submits ids it was given). Series goes through ``Series.videos``."""
    if speaker_ids:
        video.speaker.set(Speaker.objects.filter(pk__in=list(speaker_ids)))
    if topic_ids:
        video.topic.set(Topic.objects.filter(pk__in=list(topic_ids)))
    if bible_book_ids:
        video.bible_book.set(Bible_Book.objects.filter(pk__in=list(bible_book_ids)))
    if demographic_ids:
        video.demographic.set(Demographic.objects.filter(pk__in=list(demographic_ids)))
    if ministry_ids:
        video.ministry.set(Ministry.objects.filter(pk__in=list(ministry_ids)))
    if series_id:
        series = Series.objects.filter(pk=series_id).first()
        if series is not None:
            series.videos.add(video)
