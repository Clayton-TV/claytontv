"""Faceted browse: combinatorial discovery over the catalogue.

Filters AND across facets, OR within a facet (standard). Facets are the
relations that actually carry data — speaker, bible_book, demographic
(audience) — plus the talk/service split and a duration band. Ministry is
deliberately absent: the Video.ministry M2M is unpopulated in the legacy
data (0 linked), like the Video.series FK decoy. NEVER filter Video.series
(dead FK) — series membership lives only on Series.videos.
"""

from app.cards import video_card_props
from catalogue.models import Bible_Book, Demographic, Speaker, Video
from catalogue.models.video import published_count

# Duration bands in seconds: short < 15m, medium 15-40m, long >= 40m.
DURATION_BANDS = {"short": (None, 900), "medium": (900, 2400), "long": (2400, None)}
TYPE_OPTIONS = [{"value": "talk", "label": "Talks & sermons"}, {"value": "stream", "label": "Services"}]
LENGTH_OPTIONS = [
    {"value": "short", "label": "Under 15 min"},
    {"value": "medium", "label": "15 to 40 min"},
    {"value": "long", "label": "Over 40 min"},
]
TOP_SPEAKERS = 24
NT_START_ORDER = 40  # Matthew — first New Testament book by canonical order


def parse_filters(request):
    return {
        "speaker": request.GET.getlist("speaker"),
        "book": request.GET.getlist("book"),
        "audience": request.GET.getlist("audience"),
        "type": request.GET.get("type", ""),
        "length": request.GET.get("length", ""),
    }


def filtered_videos(active, ordering):
    """Build the result queryset. .distinct() because M2M __in joins multiply
    rows when a video matches several selected values in one facet."""
    qs = Video.objects.published()
    if active["speaker"]:
        qs = qs.filter(speaker__id__in=active["speaker"])
    if active["book"]:
        qs = qs.filter(bible_book__name__in=active["book"])
    if active["audience"]:
        qs = qs.filter(demographic__name__in=active["audience"])
    if active["type"] == "talk":
        qs = qs.filter(is_livestream=False)
    elif active["type"] == "stream":
        qs = qs.filter(is_livestream=True)
    band = DURATION_BANDS.get(active["length"])
    if band:
        low, high = band
        if low is not None:
            qs = qs.filter(duration_seconds__gte=low)
        if high is not None:
            qs = qs.filter(duration_seconds__lt=high)
    return qs.distinct().order_by(ordering)


def facet_options(active):
    """Option lists with global counts (approach A: stable, cacheable — counts
    reflect the whole catalogue, not the current other-facet selections, so
    the choices don't reshuffle as an elderly user clicks). Three cheap
    aggregate queries for the populated facets; type/length are fixed."""
    books = list(Bible_Book.objects.annotate(n=published_count("video")).filter(n__gt=0).order_by("order"))
    book_opts = [
        {"value": b.name, "label": b.get_name_display(), "count": b.n, "testament": "nt" if _is_nt(b) else "ot"}
        for b in books
    ]
    speakers = (
        Speaker.objects.annotate(n=published_count("video")).filter(n__gt=0).order_by("-n", "name")[:TOP_SPEAKERS]
    )
    # Always include selected speakers even if outside the top N, so chips/labels resolve
    selected_ids = set(active["speaker"])
    shown_ids = {str(s.id) for s in speakers}
    extra = Speaker.objects.filter(id__in=selected_ids - shown_ids).annotate(n=published_count("video"))
    speaker_opts = [{"value": str(s.id), "label": s.name, "count": s.n} for s in list(speakers) + list(extra)]
    audience_opts = [
        {"value": d.name, "label": d.name, "count": d.n}
        for d in Demographic.objects.annotate(n=published_count("video")).filter(n__gt=0).order_by("-n")
    ]
    return {
        "type": TYPE_OPTIONS,
        "length": LENGTH_OPTIONS,
        "audience": audience_opts,
        "book": book_opts,
        "speaker": speaker_opts,
    }


def _is_nt(book):
    # order is a stringified int; NT begins at Matthew (order 40)
    try:
        return int(book.order) >= 40
    except (TypeError, ValueError):
        return False


def browse_props(request, ordering, per_page, paginator_cls):
    active = parse_filters(request)
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginator = paginator_cls(filtered_videos(active, ordering), per_page)
    page = paginator.page(page_num)
    return {
        "title": "Browse",
        "videos": video_card_props(page.object_list),
        "facets": facet_options(active),
        "active": active,
        "total": paginator.count,
        "page": page_num,
        "num_pages": paginator.num_pages,
        "has_prev_page": page.has_previous(),
        "has_next_page": page.has_next(),
        "page_range": [p for p in paginator.get_elided_page_range(page_num, on_each_side=2, on_ends=1)],
    }
