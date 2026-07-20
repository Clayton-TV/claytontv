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
from datetime import date

from django.core.paginator import Paginator
from django.db.models import F, Min, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from app.cards import video_edit_props
from catalogue import metadata
from catalogue import search as search_index
from catalogue.models.bible_book import Bible_Book
from catalogue.models.demograpic import Demographic
from catalogue.models.ministry import Ministry
from catalogue.models.related_resource import RelatedResource
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import DRAFT, PUBLISHED, Video

logger = logging.getLogger(__name__)

# The status filter values the Library accepts (mapped to a query filter below).
STATUS_ALL = "all"
STATUS_CHOICES = (STATUS_ALL, PUBLISHED, DRAFT)

DEFAULT_PER_PAGE = 24

# Sortable Library columns. The value is the sort key the frontend sends; each
# maps to an ORDER BY expression in `_sorted` below. Speaker/series are M2M so
# they sort via an annotation; "date" mirrors the displayed coalesce of
# recorded→created. Thumbnail/actions aren't sortable.
SORT_CHOICES = ("title", "speaker", "series", "date", "status", "runtime")
SORT_DIRECTIONS = ("asc", "desc")


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
                "url": v.url,  # source URL — lets the row load the video into the player dock
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


def list_videos(*, search="", status=STATUS_ALL, page=1, per_page=DEFAULT_PER_PAGE, sort="", direction="desc"):
    """The Studio video list: filtered, searched, sorted, paginated — as plain
    dicts.

    ``sort`` is one of ``SORT_CHOICES`` (else ignored); ``direction`` is asc/desc.
    An explicit column sort takes precedence over search relevance. With no sort:
    relevance order when searching, newest-first otherwise. Returns a dict ready
    to spread into the Inertia props: ``videos``, ``total`` and pagination flags.
    """
    search = (search or "").strip()
    status = status if status in STATUS_CHOICES else STATUS_ALL
    sort = sort if sort in SORT_CHOICES else ""
    direction = direction if direction in SORT_DIRECTIONS else "desc"

    qs = Video.objects.all()
    if status != STATUS_ALL:
        qs = qs.filter(status=status)

    if search:
        ids, ordered = _search_ids(search)
        qs = qs.filter(id__in=ids)
        if ordered and not sort:
            # No explicit column sort → preserve Typesense's relevance order
            # across the (status-filtered) ids.
            position = {pk: i for i, pk in enumerate(ids)}
            objects = sorted(
                qs.prefetch_related("speaker"),
                key=lambda v: position.get(v.id, len(ids)),
            )
            return _paginate(objects, page, per_page)

    qs = qs.prefetch_related("speaker")
    # A column sort overrides the default; otherwise newest-created first — the
    # daily "what's new to flip live" view reads best most-recent-first.
    qs = _sorted(qs, sort, direction) if sort else qs.order_by("-date_created", "-id")
    return _paginate(qs, page, per_page)


def _sorted(qs, sort, direction):
    """Apply a column ORDER BY for the Library. M2M columns (speaker/series) sort
    via an annotation; "date" mirrors the displayed recorded→created coalesce.
    NULLs sort last in both directions; ``-id`` is a stable tiebreak."""
    if sort == "speaker":
        qs = qs.annotate(_sort=Min("speaker__name"))
        field = F("_sort")
    elif sort == "series":
        # Series membership is the Series.videos M2M (related_name="+", so no
        # reverse accessor) — reach it with a correlated subquery.
        qs = qs.annotate(
            _sort=Subquery(Series.objects.filter(videos=OuterRef("pk")).order_by("name").values("name")[:1])
        )
        field = F("_sort")
    elif sort == "date":
        qs = qs.annotate(_sort=Coalesce("date_recorded", "date_created"))
        field = F("_sort")
    else:
        field = F({"title": "name", "status": "status", "runtime": "duration_seconds"}[sort])

    ordering = field.desc(nulls_last=True) if direction == "desc" else field.asc(nulls_last=True)
    return qs.order_by(ordering, "-id")


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


def draft_count():
    """How many drafts are waiting in the review queue (alive only)."""
    return Video.objects.filter(status=DRAFT).count()


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
    """Soft-delete the given videos (set ``deleted_at``). Returns the number
    trashed. Recoverable via ``restore_videos`` — nothing is hard-deleted. The
    save fires the search signal, which de-indexes trashed rows."""
    trashed = 0
    for video in Video.objects.filter(id__in=list(video_ids)):
        video.deleted_at = timezone.now()
        video.save(update_fields=["deleted_at"])
        trashed += 1
    return trashed


def restore_videos(video_ids):
    """Bring soft-deleted videos back (clear ``deleted_at``). Returns the count
    restored. Reached via ``all_objects`` since the default manager hides them;
    the save re-indexes them."""
    restored = 0
    for video in Video.all_objects.filter(id__in=list(video_ids), deleted_at__isnull=False):
        video.deleted_at = None
        video.save(update_fields=["deleted_at"])
        restored += 1
    return restored


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
    # all_objects: a soft-deleted row still holds the unique URL, so a create
    # would collide with it — surface that as a duplicate too.
    existing = Video.all_objects.filter(url=(url or "").strip()).only("id", "name").first()
    return {"id": existing.id, "name": existing.name} if existing else None


def taxonomy_options():
    """Every classification choice the Add form offers, as plain ``{id, name}``
    lists keyed by relation. Small enough (a few thousand rows total) to ship to
    the page once and filter client-side."""
    return {
        "speakers": _options(Speaker),
        "series": _options(Series),
        "topics": _options(Topic),
        "bible_books": _bible_book_options(),
        "demographics": _options(Demographic),
        "ministries": _options(Ministry),
    }


def _options(model):
    return [{"id": str(pk), "name": name} for pk, name in model.objects.order_by("name").values_list("pk", "name")]


def _bible_book_options():
    """Bible books, named by their human display ("Genesis", not the stored
    "GEN" code) so the picker — and the suggestions matcher — use real names."""
    books = Bible_Book.objects.order_by("name")
    return sorted(({"id": str(b.pk), "name": b.get_name_display()} for b in books), key=lambda o: o["name"])


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
    # all_objects so a trashed row's URL (which still holds the unique constraint)
    # is treated as a duplicate rather than causing an IntegrityError.
    existing = Video.all_objects.filter(url=url).first()
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

    _apply_relations(
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


# Cap a single bulk submission so one request stays fast and quota stays sane.
BULK_MAX = 100


def expand_playlist(playlist_url):
    """A YouTube playlist URL → its video watch-URLs (raises MetadataError on a
    bad/empty/private playlist). Thin pass-through to the metadata helper."""
    return metadata.youtube_playlist_video_urls(playlist_url, max_items=BULK_MAX)


def bulk_create_from_urls(urls):
    """Create draft videos for many URLs at once. De-dupes the input, caps at
    ``BULK_MAX``, fetches metadata in a batch, then creates a draft per fresh
    URL. Returns a per-URL report plus tallies so the page can show what landed,
    what was already in the library, and what couldn't be read."""
    unique = []
    for raw in urls:
        url = (raw or "").strip()
        if url and url not in unique:
            unique.append(url)
    unique = unique[:BULK_MAX]

    fetched = metadata.fetch_metadata_many(unique)
    results = []
    for url in unique:
        outcome = fetched.get(url) or {"ok": False, "error": "Could not read that link."}
        if not outcome.get("ok"):
            results.append({"url": url, "status": "error", "error": outcome.get("error", "Could not read.")})
            continue
        meta = outcome["metadata"]
        try:
            video = create_video(
                url=meta["url"],
                name=meta["name"],
                description=meta.get("description", ""),
                thumbnail=meta.get("thumbnail"),
                duration_seconds=meta.get("duration_seconds"),
                date_recorded=meta.get("date_recorded"),
                status=DRAFT,
            )
        except DuplicateVideoError as exc:
            results.append({"url": url, "status": "duplicate", "name": exc.video.name, "id": exc.video.id})
            continue
        results.append({"url": url, "status": "created", "name": video.name, "id": video.id})

    tally = {"created": 0, "duplicate": 0, "error": 0}
    for r in results:
        tally[r["status"]] += 1
    return {
        "results": results,
        "created": tally["created"],
        "duplicates": tally["duplicate"],
        "errors": tally["error"],
    }


def _mint_video_id():
    """A unique, non-colliding primary key for a Studio-created video.

    Legacy ids are bare numeric strings; ours are ``S`` + a zero-padded counter
    (``S0000001``) so they never clash with a legacy id — even one the dying
    live-admin feed imports later — and fit the 10-char ``id`` column.
    """
    # all_objects: trashed S-rows still occupy their primary key, so they must
    # count toward uniqueness or we'd mint a colliding id.
    n = Video.all_objects.filter(id__startswith="S").count() + 1
    while True:
        candidate = f"S{n:07d}"
        if not Video.all_objects.filter(Q(id=candidate) | Q(id_number=candidate)).exists():
            return candidate
        n += 1


def _apply_relations(video, *, speaker_ids, topic_ids, bible_book_ids, demographic_ids, ministry_ids, series_id):
    """Set the M2M classifications to exactly the given ids — ``.set()`` so the
    editor can *remove* relations, not only add (create passes the same shape, so
    empty lists clear correctly). Unknown ids are silently dropped. Series goes
    through the ``Series.videos`` M2M (re-pointed: dropped from any other series,
    added to the chosen one), never the decoy ``Video.series`` FK."""
    video.speaker.set(Speaker.objects.filter(pk__in=list(speaker_ids or [])))
    video.topic.set(Topic.objects.filter(pk__in=list(topic_ids or [])))
    video.bible_book.set(Bible_Book.objects.filter(pk__in=list(bible_book_ids or [])))
    video.demographic.set(Demographic.objects.filter(pk__in=list(demographic_ids or [])))
    video.ministry.set(Ministry.objects.filter(pk__in=list(ministry_ids or [])))

    for series in Series.objects.filter(videos=video):
        if str(series.pk) != str(series_id):
            series.videos.remove(video)
    if series_id:
        target = Series.objects.filter(pk=series_id).first()
        if target is not None:
            target.videos.add(video)


# --------------------------------------------------------------------------- #
# Edit a video (Slice 4a)
# --------------------------------------------------------------------------- #


def get_video_for_edit(video_id):
    """The full editable view of one video (plain dict), or None if missing."""
    video = (
        Video.objects.filter(id=video_id)
        .select_related("enrichment")
        .prefetch_related("speaker", "topic", "bible_book", "demographic", "ministry", "related_resources")
        .first()
    )
    return video_edit_props(video) if video is not None else None


def update_video(
    video_id,
    *,
    name,
    description="",
    url,
    thumbnail=None,
    duration_seconds=None,
    date_recorded=None,
    is_livestream=False,
    number_in_series=None,
    speaker_ids=(),
    topic_ids=(),
    bible_book_ids=(),
    demographic_ids=(),
    ministry_ids=(),
    series_id=None,
    alternate_urls=None,
    related_resources=None,
):
    """Update an existing video's scalar fields, classification, alternate URLs
    and related resources. Returns True, or False if the id doesn't exist.

    Publication status is NOT touched here — that goes through ``set_video_status``
    (the editor's Publish/Unpublish buttons), keeping Save status-neutral. Raises
    ``DuplicateVideoError`` if ``url`` is changed to one another video already uses
    (``Video.url`` is unique)."""
    video = Video.objects.filter(id=video_id).first()
    if video is None:
        return False

    url = (url or "").strip()
    clash = Video.all_objects.filter(url=url).exclude(id=video_id).first()
    if clash is not None:
        raise DuplicateVideoError(clash)

    video.name = (name or "").strip()[:200] or video.name
    video.description = description or ""
    video.url = url
    video.thumbnail = thumbnail
    video.duration_seconds = duration_seconds
    video.date_recorded = _parse_date(date_recorded)
    video.is_livestream = bool(is_livestream)
    video.number_in_series = number_in_series
    video.alternate_urls = alternate_urls or []

    _apply_relations(
        video,
        speaker_ids=speaker_ids,
        topic_ids=topic_ids,
        bible_book_ids=bible_book_ids,
        demographic_ids=demographic_ids,
        ministry_ids=ministry_ids,
        series_id=series_id,
    )
    _sync_resources(video, related_resources or [])
    # Single save after relations are set so the search signal re-indexes a doc
    # that reflects the new scalars + facets.
    video.save()
    return True


def _parse_date(value):
    """An ISO ``YYYY-MM-DD`` string (or date) → a date, else None."""
    if not value:
        return None
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


_RESOURCE_KINDS = {kind for kind, _ in RelatedResource.KINDS}


def _sync_resources(video, resources):
    """Make ``video.related_resources`` match the given ``[{kind, url}]`` list:
    drop rows no longer present, create the new ones. Skips invalid/blank rows."""
    wanted = {
        (r.get("kind"), (r.get("url") or "").strip())
        for r in resources
        if r.get("kind") in _RESOURCE_KINDS and (r.get("url") or "").strip()
    }
    existing = {(r.kind, r.url): r for r in video.related_resources.all()}
    for key, row in existing.items():
        if key not in wanted:
            row.delete()
    for kind, url in wanted:
        if (kind, url) not in existing:
            RelatedResource.objects.create(video=video, kind=kind, url=url)
