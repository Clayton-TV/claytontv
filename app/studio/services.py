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

from catalogue import search as search_index
from catalogue.models.series import Series
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
