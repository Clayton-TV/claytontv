import logging
import math
from collections import Counter
from urllib.parse import unquote  # Import for URL decoding

import sentry_sdk
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import Http404, JsonResponse
from inertia import defer, optional, render

from app.auth import can_edit_content
from app.browse import browse_props
from app.cards import video_card_props
from app.feed import latest_feed
from app.sanitize import sanitize_description
from catalogue import search as search_index
from catalogue.ingest.normalize import clean_name, clean_topic_name
from catalogue.models.bible_book import Bible_Book
from catalogue.models.channel import Channel
from catalogue.models.demograpic import Demographic
from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import PUBLISHED, Video, published_count
from catalogue.passages import parse_passage, passage_label
from catalogue.youtube_live import homepage_live_props, live_streams, upcoming_streams

pagination_per_page = 24

logger = logging.getLogger(__name__)

# Newest first with undated entries at the END on both engines: Postgres
# defaults DESC to NULLS FIRST (undated videos would top every rail),
# SQLite to nulls last — the mismatch hid this locally.
RECENT_FIRST = F("date_recorded").desc(nulls_last=True)

# Index `kind` → the display label each surface uses. The palette and the search
# page label the same kinds differently (kept for output parity).
PALETTE_KIND_LABELS = {
    search_index.KIND_SERIES: "Series",
    search_index.KIND_SPEAKER: "Speaker",
    search_index.KIND_TOPIC: "Topic",
    search_index.KIND_MINISTRY: "Ministry",
    search_index.KIND_BOOK: "Book",
}
SEARCH_KIND_LABELS = {
    search_index.KIND_CHANNEL: "Channels",
    search_index.KIND_AUDIENCE: "Demographics",
    search_index.KIND_MINISTRY: "Ministries",
    search_index.KIND_SERIES: "Series",
    search_index.KIND_SPEAKER: "Speakers",
    search_index.KIND_TOPIC: "Topics",
    search_index.KIND_BOOK: "Bible Book",
}
# Per-kind cap for the full search page (the ORM path is uncapped; Typesense
# ranks by relevance so a generous cap keeps the chip list useful but bounded).
SEARCH_CATEGORY_LIMIT = 20


def index(request):
    """Curated homepage: a few of the latest videos, a handful of featured
    series and topics. Everything else is one click deeper — the previous
    everything-dump shipped ~300 kB of props and 1,069 series cards.

    `livestreams`/`next_service` come from the LiveStream table kept fresh by
    the sync_live_streams command (Epic 4). Series counts use the
    Series.videos M2M (what link_series populates); topic counts use the
    reverse of Video.topic (what link_videos populates).
    """
    latest_videos = Video.objects.published().filter(is_livestream=False).order_by(RECENT_FIRST)[:6]
    live_now, next_service = homepage_live_props()

    def featured_series():
        return [
            {
                "name": s.name,
                "summary": s.summary,
                "videosCount": s.videos_count,
                "url": s.get_absolute_url(),
            }
            for s in Series.objects.annotate(videos_count=published_count("videos"))
            .filter(videos_count__gt=0)
            .order_by("-videos_count")[:4]
        ]

    def topics_data():
        return [
            {
                "name": t.name,
                "videosCount": t.videos_count,
                "url": t.get_absolute_url(),
            }
            for t in Topic.objects.annotate(videos_count=published_count("video"))
            .filter(videos_count__gt=0)
            .order_by("-videos_count")[:12]
        ]

    return render(
        request,
        "Welcome",
        {
            "livestreams": live_now,
            "next_service": next_service,
            "latest_videos": video_card_props(latest_videos),
            # Below-the-fold sections load when scrolled into view (WhenVisible):
            # their queries don't run at all on first paint.
            "featured_series": optional(featured_series),
            "topics_data": optional(topics_data),
            "topics_total": optional(lambda: Topic.objects.count()),
        },
    )


def browse_all_livestreams(request):
    """The Services destination: live now + upcoming scheduled services + the
    past-services archive in one place (Epic 4). One obvious page for the
    Sunday service, calm when nothing is on."""
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    livestreams = Video.objects.published().filter(is_livestream=True).order_by(RECENT_FIRST)
    paginator = Paginator(livestreams, pagination_per_page)
    paginated = paginator.page(page_num)
    return render(
        request,
        "Services",
        {
            "title": "Services",
            "live": live_streams(),
            "upcoming": upcoming_streams(),
            "past": video_card_props(paginated.object_list),
            "page": page_num,
            "num_pages": paginator.num_pages,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def browse_all_latest(request):
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    return render(request, "LatestFeed", {"title": "Latest", **latest_feed(page_num)})


def next_in_series(video_object, series=None):
    """The episode after this one in course order, or None at the end.

    Series→video links live on the Series.videos M2M (no reverse accessor
    from Video: related_name="+"). Course order matches the series page,
    sorted in Python because SQLite and Postgres disagree on where NULL
    episode numbers land.
    """
    series = series or Series.objects.filter(videos=video_object).first()
    if series is None:
        return None
    episodes = list(series.videos.filter(status=PUBLISHED))
    episodes.sort(
        key=lambda v: (
            v.number_in_series is None,
            v.number_in_series or 0,
            v.date_recorded or v.date_created,
            v.id,
        )
    )
    ids = [v.id for v in episodes]
    if video_object.id not in ids:  # e.g. a draft asking for its "next" — none publicly
        return None
    position = ids.index(video_object.id)
    return episodes[position + 1] if position + 1 < len(episodes) else None


def video_next(request, id):
    """JSON next-episode lookup so the mini-player can chain episodes while
    the viewer browses elsewhere — no page navigation involved."""
    try:
        video_object = Video.objects.get(id=id)
    except Video.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)
    following = next_in_series(video_object)
    return JsonResponse({"next": video_card_props([following])[0] if following else None})


PALETTE_LIMIT = 6


def palette(request):
    """Grouped name-only search for the ⌘K command palette. Fired on every
    keystroke, so: hard caps, JSON not Inertia. Served by Typesense (typo- and
    synonym-tolerant) with a graceful ORM fallback so it never hard-fails."""
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"videos": [], "categories": []})

    try:
        payload = _palette_typesense(query)
    except search_index.SearchUnavailableError as exc:
        logger.info("palette: Typesense unavailable, using ORM fallback (%s)", exc)
        payload = _palette_orm(query)
    except Exception:
        logger.warning("palette: Typesense proxy error, using ORM fallback", exc_info=True)
        sentry_sdk.capture_exception()
        payload = _palette_orm(query)

    return JsonResponse(payload)


def _palette_typesense(query):
    video_hits, _ = search_index.search_videos(query, page=1, per_page=PALETTE_LIMIT)
    videos = [{"id": h.pk, "name": h.name, "url": h.url, "date": h.date_display} for h in video_hits]

    categories = [
        {"kind": PALETTE_KIND_LABELS[h.kind], "name": h.name, "url": h.url, "count": h.videos_count}
        for h in search_index.search_categories(query, kinds=list(PALETTE_KIND_LABELS), per_kind=PALETTE_LIMIT)
    ]
    return {"videos": videos, "categories": categories}


def _palette_orm(query):
    """Name-only ORM search — the fallback when Typesense is unavailable."""
    videos = [
        {"id": v.id, "name": v.name, "url": f"/video/{v.id}", "date": v.date_recorded or v.date_created}
        for v in Video.objects.published().filter(name__icontains=query).order_by(RECENT_FIRST)[:PALETTE_LIMIT]
    ]

    categories = []
    for model, kind in [(Series, "Series"), (Speaker, "Speaker"), (Topic, "Topic"), (Ministry, "Ministry")]:
        # Series videos live on the Series.videos M2M, not the FK reverse
        count_relation = "videos" if model is Series else "video"
        matches = model.objects.filter(name__icontains=query).annotate(n=published_count(count_relation)).order_by("-n")
        # Topic names carry depth-prefix mojibake; others just stray whitespace.
        clean_label = clean_topic_name if model is Topic else clean_name
        categories += [
            {"kind": kind, "name": clean_label(m.name), "url": m.get_absolute_url(), "count": m.n}
            for m in matches[:PALETTE_LIMIT]
        ]
    # Book names are choice codes; the display name lives in summary
    books = Bible_Book.objects.filter(summary__icontains=query).annotate(n=published_count("video"))[:PALETTE_LIMIT]
    categories += [
        {"kind": "Book", "name": b.get_name_display(), "url": b.get_absolute_url(), "count": b.n} for b in books
    ]

    return {"videos": videos, "categories": categories}


def browse_faceted(request):
    """Combinatorial discovery surface (see app/browse.py). Coexists with the
    single-relation browse_* pages, which stay as pre-filtered entry points."""
    return render(request, "BrowseFaceted", browse_props(request, RECENT_FIRST, pagination_per_page, Paginator))


def search(request):
    """Full-page search. Served by Typesense (relevance-ranked, typo- and
    synonym-tolerant) with a graceful ORM fallback so search never hard-fails.
    Categories appear on page 1 only; both engines return the same prop shape."""
    searchquery = request.GET.get("search", "").strip()
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1

    # No term at all (a bookmark of /search, a stripped link, a crawler): show the
    # empty page rather than asking either engine for everything.
    if not searchquery:
        return render(
            request,
            "Search",
            {
                "title": "Search",
                "description": "Type a word, a speaker's name, or a Bible book to find videos.",
                "videos": [],
                "categories": [],
                "has_prev_page": False,
                "has_next_page": False,
            },
        )

    try:
        props = _search_typesense(searchquery, page_num)
    except search_index.SearchUnavailableError as exc:
        logger.info("search: Typesense unavailable, using ORM fallback (%s)", exc)
        props = _search_orm(searchquery, page_num)
    except Exception:
        logger.warning("search: Typesense proxy error, using ORM fallback", exc_info=True)
        sentry_sdk.capture_exception()
        props = _search_orm(searchquery, page_num)

    return render(request, "Search", props)


def _search_typesense(searchquery, page_num):
    hits, found = search_index.search_videos(searchquery, page=page_num, per_page=pagination_per_page)
    # Hydrate the ranked ids in one query, preserving Typesense's relevance order.
    by_id = {str(v.id): v for v in Video.objects.published().filter(id__in=[h.pk for h in hits])}
    ordered = [by_id[h.pk] for h in hits if h.pk in by_id]

    total_pages = max(1, math.ceil(found / pagination_per_page))
    props = {
        "title": f"Search for '{searchquery}'",
        "description": f"Found {found} {'video' if found == 1 else 'videos'} (page {page_num} of {total_pages})",
        "videos": video_card_props(ordered),
        "has_prev_page": page_num > 1,
        "has_next_page": page_num * pagination_per_page < found,
    }
    if page_num == 1:
        cat_hits = search_index.search_categories(
            searchquery, kinds=list(SEARCH_KIND_LABELS), per_kind=SEARCH_CATEGORY_LIMIT
        )
        props["categories"] = [
            {"category": SEARCH_KIND_LABELS[h.kind], "name": h.name, "videosCount": h.videos_count, "url": h.url}
            for h in cat_hits
        ]
    return props


def _search_orm(searchquery, page_num):
    """ORM ``icontains`` search — the fallback when Typesense is unavailable."""
    video_results = []
    video_results += Video.objects.published().filter(name__icontains=searchquery)
    video_results += [
        v for v in Video.objects.published().filter(description__icontains=searchquery) if v not in video_results
    ]
    paginator = Paginator(video_results, pagination_per_page)
    paginated = paginator.page(page_num)
    description = (
        f"Found {len(video_results)} {'video' if len(video_results) == 1 else 'videos'} "
        f"(page {page_num} of {paginator.num_pages})"
    )
    props = {
        "title": f"Search for '{searchquery}'",
        "description": description,
        "videos": video_card_props(paginated.object_list),
        "has_prev_page": paginated.has_previous(),
        "has_next_page": paginated.has_next(),
    }
    if page_num == 1:
        category_results = []
        for model, model_name in [
            (Channel, "Channels"),
            (Demographic, "Demographics"),
            (Ministry, "Ministries"),
            (Series, "Series"),
            (Speaker, "Speakers"),
            (Topic, "Topics"),
        ]:
            matches = model.objects.filter(name__icontains=searchquery)
            # Series videos live on the Series.videos M2M, not the FK reverse
            count_relation = "videos" if model is Series else "video"
            matches = matches.annotate(n=published_count(count_relation))
            # Topic names carry depth-prefix mojibake; others just stray whitespace.
            clean_label = clean_topic_name if model is Topic else clean_name
            category_results += [
                {
                    "category": model_name,
                    "name": clean_label(x.name),
                    "videosCount": x.n,
                    "url": x.get_absolute_url(),
                }
                for x in matches
            ]
        category_results += [
            {
                "category": "Bible Book",
                "name": x.get_name_display(),
                "videosCount": x.n,
                "url": x.get_absolute_url(),
            }
            for x in Bible_Book.objects.filter(summary__icontains=searchquery).annotate(n=published_count("video"))
        ]
        props["categories"] = category_results
    return props


def video(request, id):  # noqa: C901 — pre-existing watch-page assembler; the draft guard adds one branch
    try:
        # Prefetch the M2M relations the metadata + passage blocks walk, so the
        # watch page's initial render stays a handful of queries (bible_book in
        # particular is iterated twice).
        video_object = (
            Video.objects.select_related("channel")
            .prefetch_related("topic", "ministry", "speaker", "bible_book", "demographic")
            .get(id=id)
        )
        # Drafts are not public — only editors/staff may preview them.
        if video_object.status != PUBLISHED and not can_edit_content(request.user):
            raise Http404
        video_metadata = {}
        # The Video.series FK is never populated; membership lives on Series.videos
        video_series = Series.objects.filter(videos=video_object).first()
        # Properties to interrogate, with boolean for whether they are plural (True) or singular (False)
        props = {
            "topic": (video_object.topic, True),
            "channel": (video_object.channel, False),
            "series": (video_series, False),
            "ministry": (video_object.ministry, True),
            "speaker": (video_object.speaker, True),
            "bible_book": (video_object.bible_book, True),
            "demographic": (video_object.demographic, True),
        }
        for p in props:
            if props[p][0] is not None:
                if props[p][1]:
                    if p == "bible_book":
                        video_metadata[p] = [
                            {"name": i.summary, "url": i.get_absolute_url()} for i in props[p][0].all()
                        ]
                    else:
                        video_metadata[p] = [{"name": i.name, "url": i.get_absolute_url()} for i in props[p][0].all()]
                else:
                    video_metadata[p] = {"name": props[p][0].name, "url": props[p][0].get_absolute_url()}

        # Passage badge: the first linked book whose chapter we can read from
        # the title (e.g. "Luke 15:11-24"), linking to that chapter's teaching.
        passage_badge = None
        for book in video_object.bible_book.all():
            parsed = parse_passage(video_object.name, book.get_name_display())
            if parsed:
                passage_badge = {
                    "label": f"{book.get_name_display()} {passage_label(parsed)}",
                    "url": f"{book.get_absolute_url()}?chapter={parsed['chapter']}",
                }
                break

        # Rescued related resources (transcript/audio reference links)
        resources = [{"kind": r.kind, "url": r.url} for r in video_object.related_resources.order_by("kind")]

        def up_next():
            series = Series.objects.filter(videos=video_object).first()
            if series is None:
                return None
            following = next_in_series(video_object, series)
            return {
                "series": {"name": series.name, "url": series.get_absolute_url()},
                "videos": video_card_props(
                    series.videos.filter(status=PUBLISHED).exclude(id=video_object.id).order_by(RECENT_FIRST)[:6]
                ),
                # The episode autoplay advances to when this one ends
                "next": video_card_props([following])[0] if following else None,
            }

        return render(
            request,
            "WatchVideo",
            {
                # A plain dict, never the model: serializing a Video follows its
                # M2M relations (series → demographic → video → …) and recurses
                # forever under SSR. Mirror video_card_props' raw-field approach.
                "video": {
                    "id": video_object.id,
                    "name": video_object.name,
                    "url": video_object.url,
                    # Legacy descriptions carry raw HTML rendered via v-html;
                    # sanitize before it reaches the client (issue #110).
                    "description": sanitize_description(video_object.description),
                    "date_recorded": video_object.date_recorded,
                    "date_created": video_object.date_created,
                    "duration_seconds": video_object.duration_seconds,
                    "is_livestream": video_object.is_livestream,
                },
                "video_metadata": video_metadata,
                "passage": passage_badge,
                "resources": resources,
                # Deferred: the player paints immediately; the rail streams in
                # right after via the Inertia v3 deferred-props round trip.
                "up_next": defer(up_next),
            },
        )
    except Video.DoesNotExist:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": "Video not found",
                "description": f"Error retreiving video data for id: '{id}'",
            },
        )


def browse_bible_book(request, id):
    decoded_id = unquote(id)

    bible_book = Bible_Book.objects.filter(name=decoded_id).first()
    if bible_book is None:
        return render(request, "Browse", {"videos": [], "title": f"Bible book not found: '{decoded_id}'"})

    book_name = bible_book.get_name_display()
    all_videos = list(bible_book.video_set.filter(status=PUBLISHED).order_by(RECENT_FIRST))

    # Derive the passage from each title; teaching that names a chapter is
    # ordered by chapter (a book reads in order), the rest ("topical") trails.
    decorated = []
    chapters = set()
    for video in all_videos:
        passage = parse_passage(video.name, book_name)
        if passage:
            chapters.add(passage["chapter"])
        decorated.append((video, passage))

    selected_chapter = request.GET.get("chapter")
    selected = int(selected_chapter) if (selected_chapter or "").isdigit() else None
    if selected is not None:
        decorated = [(v, p) for v, p in decorated if p and p["chapter"] == selected]

    # Chapter first (None last), then most recent — a passage-ordered reading list
    decorated.sort(key=lambda dp: (dp[1] is None, dp[1]["chapter"] if dp[1] else 0))

    def card(video, passage):
        props = video_card_props([video])[0]
        props["reference"] = passage_label(passage)
        return props

    return render(
        request,
        "BookDetail",
        {
            "book": {
                "name": book_name,
                "summary": bible_book.summary,
                "section": bible_book.get_type_display(),
                "videosCount": len(all_videos),
            },
            "chapters": sorted(chapters),
            "selected_chapter": selected,
            "videos": [card(v, p) for v, p in decorated],
        },
    )


def browse_channel(request, id):
    decoded_id = unquote(id)

    try:
        channel = Channel.objects.get(name=decoded_id)
    except Channel.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Channel not found: '{decoded_id}'",
                "description": f"Error retreiving channel data: '{e}'",
            },
        )

    paginator = Paginator(channel.video_set.filter(status=PUBLISHED), pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)
    return render(
        request,
        "Browse",
        {
            "title": f"Channel: {decoded_id}",
            "description": f"{channel.summary} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def browse_demographic(request, id):
    decoded_id = unquote(id)

    try:
        demographic = Demographic.objects.get(name=decoded_id)
    except Demographic.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Demographic not found: '{decoded_id}'",
                "description": f"Error retreiving demographic data: '{e}'",
            },
        )

    paginator = Paginator(demographic.video_set.filter(status=PUBLISHED), pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)
    return render(
        request,
        "Browse",
        {
            "title": f"Demographic: {decoded_id}",
            "description": f"{demographic.summary} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def browse_ministry(request, id):
    decoded_id = unquote(id)

    try:
        ministry = Ministry.objects.get(name=decoded_id)
    except Ministry.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Ministry not found: '{decoded_id}'",
                "description": f"Error retreiving ministry data: '{e}'",
            },
        )

    paginator = Paginator(ministry.video_set.filter(status=PUBLISHED), pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)
    return render(
        request,
        "Browse",
        {
            "title": f"Ministry: {decoded_id}",
            "description": f"{ministry.summary} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def series_index(request):
    """All series as course-style cards: filterable, paginated, most-watched-in first."""
    query = request.GET.get("q", "").strip()
    series_qs = (
        Series.objects.annotate(videos_count=published_count("videos"))
        .filter(videos_count__gt=0)
        .order_by("-videos_count", "name")
    )
    if query:
        series_qs = series_qs.filter(name__icontains=query)

    paginator = Paginator(series_qs, pagination_per_page)
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)

    return render(
        request,
        "SeriesIndex",
        {
            "series": [
                {
                    "name": s.name,
                    "summary": s.summary,
                    "videosCount": s.videos_count,
                    "url": s.get_absolute_url(),
                }
                for s in paginated.object_list
            ],
            "query": query,
            "total": paginator.count,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def topics_index(request):
    """All topics grouped under the legacy taxonomy's parent categories.

    The legacy data leaks two blemishes here (Phase 6): category strings have
    case-typo and whitespace near-duplicates ('Christian Life' vs the typo
    'Christian LIfe'), and topic names carry depth-prefix mojibake. Merge
    categories on a case-folded key (showing the most common spelling) and
    strip the prefixes from names."""
    groups = {}  # folded key -> {"labels": Counter, "topics": [...]}
    for topic in Topic.objects.annotate(videos_count=published_count("video")).order_by("name"):
        category = clean_name(topic.category) or "Other"
        group = groups.setdefault(category.casefold(), {"labels": Counter(), "topics": []})
        group["labels"][category] += 1
        group["topics"].append(
            {
                "name": clean_topic_name(topic.name),
                "videosCount": topic.videos_count,
                "url": topic.get_absolute_url(),
            }
        )

    topic_groups = []
    for group in groups.values():
        group["topics"].sort(key=lambda topic: topic["name"].casefold())
        topic_groups.append({"category": group["labels"].most_common(1)[0][0], "topics": group["topics"]})
    topic_groups.sort(key=lambda group: group["category"].casefold())

    return render(
        request,
        "TopicsIndex",
        {
            # Audiences moved to their own /audience/ area (TopicsIndex shows a
            # pointer link instead of folding them in here).
            "topic_groups": topic_groups,
            "total": Topic.objects.count(),
        },
    )


def audiences_index(request):
    """Dedicated audiences landing (Kids/Youth/Adults) — image-led tiles for
    the parent/kids persona, its own nav area rather than buried in Topics."""
    audiences = [
        {
            "name": d.name,
            "summary": d.summary,
            "thumbnail": d.thumbnail,
            "videosCount": d.videos_count,
            "url": d.get_absolute_url(),
        }
        for d in Demographic.objects.annotate(videos_count=published_count("video"))
        .filter(videos_count__gt=0)
        .order_by("-videos_count")
    ]
    return render(request, "AudiencesIndex", {"audiences": audiences})


def speakers_index(request):
    """Lookup-first speaker page (per docs/DESIGN_SPEC.md): a search hero for
    "do you have X?", a curated featured tier for discovery, and the 600-name
    long tail as a compact scroll-deferred A-Z list — never a card dump."""
    query = request.GET.get("q", "").strip()
    base = Speaker.objects.annotate(videos_count=published_count("video")).filter(videos_count__gt=0)
    total = base.count()

    def entry(speaker):
        return {"name": speaker.name, "videosCount": speaker.videos_count, "url": speaker.get_absolute_url()}

    if query:
        return render(
            request,
            "SpeakersIndex",
            {
                "query": query,
                "total": total,
                "results": [entry(s) for s in base.filter(name__icontains=query).order_by("name")[:60]],
            },
        )

    featured = []
    for speaker in base.order_by("-videos_count")[:8]:
        top_series = (
            Series.objects.filter(videos__speaker=speaker)
            .annotate(n=Count("videos", filter=Q(videos__speaker=speaker, videos__status=PUBLISHED)))
            .order_by("-n")
            .first()
        )
        featured.append({**entry(speaker), "knownFor": top_series.name if top_series else None})

    def all_speakers():
        groups = {}
        for speaker in base.order_by("name"):
            groups.setdefault(speaker.name[0].upper(), []).append(entry(speaker))
        return [{"letter": letter, "speakers": speakers} for letter, speakers in sorted(groups.items())]

    return render(
        request,
        "SpeakersIndex",
        {
            "query": "",
            "total": total,
            "featured": featured,
            # The full directory loads only when scrolled to (WhenVisible)
            "all_speakers": optional(all_speakers),
        },
    )


def books_index(request):
    """All 66 Bible books in canonical order, grouped by section."""
    groups = {}
    books = Bible_Book.objects.annotate(videos_count=published_count("video"))
    for book in sorted(books, key=lambda b: int(b.order) if str(b.order).isdigit() else 999):
        groups.setdefault(book.get_type_display(), []).append(
            {
                "name": book.get_name_display(),
                "videosCount": book.videos_count,
                "url": book.get_absolute_url(),
            }
        )

    return render(
        request,
        "BooksIndex",
        {
            # Insertion order is canonical order (groups were filled from sorted books)
            "book_groups": [{"section": section, "books": books} for section, books in groups.items()],
        },
    )


def ministries_index(request):
    """All ministries and churches with content, alphabetically."""
    rows = Ministry.objects.annotate(videos_count=published_count("video")).filter(videos_count__gt=0).order_by("name")
    ministries = [
        {
            "name": m.name,
            "summary": m.summary,
            "videosCount": m.videos_count,
            "url": m.get_absolute_url(),
        }
        for m in rows
    ]

    return render(
        request,
        "MinistriesIndex",
        {
            "ministries": ministries,
            "total": len(ministries),
        },
    )


def browse_series(request, id):
    decoded_id = unquote(id)

    # Canonical route is by id_number (names collide); old name-based links
    # still resolve as a fallback.
    series_qs = Series.objects.annotate(videos_count=published_count("videos"))
    try:
        series = series_qs.filter(id_number=decoded_id).first() or series_qs.filter(name=decoded_id).first()
        if series is None:
            raise Series.DoesNotExist(f"No series with id or name '{decoded_id}'")
    except Series.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Series not found: '{decoded_id}'",
                "description": f"Error retreiving series data: '{e}'",
            },
        )

    # Episodes live on the Series.videos M2M (the video_set FK reverse is never
    # populated). Order by episode number where ingestion assigned one, oldest
    # first — a course reads start-to-finish, not newest-first.
    episodes = series.videos.filter(status=PUBLISHED).order_by("number_in_series", "date_recorded")
    paginator = Paginator(episodes, 50)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)

    start_episode = episodes.first()
    # Total runtime across the whole series (all pages), where durations exist.
    total_runtime = series.videos.filter(status=PUBLISHED).aggregate(total=Sum("duration_seconds"))["total"]
    return render(
        request,
        "SeriesDetail",
        {
            "series_meta": {
                "name": series.name,
                "summary": series.summary,
                "videosCount": series.videos_count,
                "total_runtime": total_runtime,
                "year_start": series.year_start,
                "year_end": series.year_end,
            },
            "start_url": f"/video/{start_episode.id}" if start_episode else None,
            "episodes": [
                {
                    "id": v.id,
                    "name": v.name,
                    "number": v.number_in_series,
                    "url": f"/video/{v.id}",
                    "date": v.date_recorded.isoformat() if v.date_recorded else None,
                    "thumbnail": v.thumbnail,
                    "duration_seconds": v.duration_seconds,
                }
                for v in paginated.object_list
            ],
            "page_start": (page_num - 1) * 50,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def browse_speaker(request, id):
    decoded_id = unquote(id)

    # Speaker names are unique; id is the stable fallback for future links.
    speaker = Speaker.objects.filter(name=decoded_id).first() or Speaker.objects.filter(id=decoded_id).first()
    if speaker is None:
        return render(
            request,
            "Browse",
            {"videos": [], "title": f"Speaker not found: '{decoded_id}'"},
        )

    talks = speaker.video_set.filter(status=PUBLISHED).order_by(RECENT_FIRST)
    paginator = Paginator(talks, pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)

    def series():
        # Series this speaker features in: series whose videos include theirs.
        return [
            {"name": s.name, "summary": s.summary, "videosCount": s.videos_count, "url": s.get_absolute_url()}
            for s in Series.objects.filter(videos__speaker=speaker)
            .distinct()
            .annotate(videos_count=published_count("videos"))
            .order_by("-videos_count")[:6]
        ]

    return render(
        request,
        "SpeakerDetail",
        {
            "speaker": {"name": speaker.name, "bio": speaker.bio, "talksCount": paginator.count},
            # defer() (not optional): the <Deferred> component auto-loads it
            # right after first paint, so the page shows talks immediately.
            "series": defer(series),
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def browse_topic(request, id):
    decoded_id = unquote(id)

    try:
        topic = Topic.objects.get(name=decoded_id)
    except Topic.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Topic not found: '{decoded_id}'",
                "description": f"Error retreiving topic data: '{e}'",
            },
        )

    paginator = Paginator(topic.video_set.filter(status=PUBLISHED), pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)
    return render(
        request,
        "Browse",
        {
            "title": f"Topic: {decoded_id}",
            "description": f"{topic.summary} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
            "num_pages": paginator.num_pages,
        },
    )


def browse_categories(request):
    category = request.path.strip("/")
    categories_data = None
    title = None
    description = None
    single_parent_category = False
    categories_sort_order = "alphabetical"
    subcategories_sort_order = "alphabetical"

    if category == "book":
        categories_data = [
            {
                "category": b.type,
                "name": b.get_name_display(),
                "videosCount": b.videos_count,
                "url": b.get_absolute_url(),
            }
            for b in Bible_Book.objects.annotate(videos_count=published_count("video"))
        ]
        title = "Bible Books"
        description = "Browsing all Bible books"
        single_parent_category = True
        categories_sort_order = "none"

    elif category == "channel":
        categories_data = [
            {
                "category": ("Primary (Trusted)" if c.trusted else "Secondary (Untrusted)"),
                "name": c.name,
                "videosCount": c.videos_count,
                "url": c.get_absolute_url(),
            }
            for c in Channel.objects.annotate(videos_count=published_count("video"))
        ]
        title = "Channels"
        description = "Browsing all known channels"
        single_parent_category = True
        categories_sort_order = "none"

    elif category == "demographic":
        categories_data = [
            {
                "category": "All",
                "name": d.name,
                "videosCount": d.videos_count,
                "url": d.get_absolute_url(),
            }
            for d in Demographic.objects.annotate(videos_count=published_count("video"))
        ]
        title = "Demographic"
        description = "Browsing all known demographics"
        single_parent_category = True

    elif category == "ministry":
        categories_data = [
            {
                "category": [c.name for c in m.channel.all() if c.name is not None],
                "name": m.name,
                "videosCount": m.videos_count,
                "url": m.get_absolute_url(),
            }
            for m in Ministry.objects.annotate(videos_count=published_count("video")).prefetch_related("channel")
        ]
        title = "Ministries"
        description = "Browsing all known ministries"

    elif category == "speaker":
        # The per-speaker channel grouping cost a query per speaker (693 of
        # them); a flat alphabetical list serves the lookup use case better.
        categories_data = [
            {
                "category": "All",
                "name": s.name,
                "videosCount": s.videos_count,
                "url": s.get_absolute_url(),
            }
            for s in Speaker.objects.annotate(videos_count=published_count("video"))
        ]
        title = "Speakers"
        description = "Browsing all known speakers"
        single_parent_category = True

    if categories_data is not None:
        return render(
            request,
            "CategoriesBrowsePage",
            {
                "categories_data": categories_data,
                "title": title,
                "description": description,
                "single_parent_category": single_parent_category,
                "categories_sort_order": categories_sort_order,
                "subcategories_sort_order": subcategories_sort_order,
            },
        )
