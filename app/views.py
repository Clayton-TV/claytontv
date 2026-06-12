from urllib.parse import unquote  # Import for URL decoding

from django.core.paginator import Paginator
from django.db.models import Count
from inertia import defer, optional, render

from catalogue.models.bible_book import Bible_Book
from catalogue.models.channel import Channel
from catalogue.models.demograpic import Demographic
from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import Video

pagination_per_page = 24

VIDEO_CARD_FIELDS = ("id", "name", "url", "thumbnail", "date_recorded", "date_created", "is_livestream")


def video_card_props(videos):
    """Serialize videos to the fields the card components render.

    Passing full Video objects to Inertia serializes every M2M relation,
    costing ~5 extra queries per video.
    """
    if hasattr(videos, "values"):
        return list(videos.values(*VIDEO_CARD_FIELDS))
    return [{field: getattr(video, field) for field in VIDEO_CARD_FIELDS} for video in videos]


def index(request):
    """Curated homepage: a few of the latest videos, a handful of featured
    series and topics. Everything else is one click deeper — the previous
    everything-dump shipped ~300 kB of props and 1,069 series cards.

    `livestreams` is for genuinely live/upcoming broadcasts (YouTube API,
    Epic 4); until then it stays empty rather than presenting recordings as
    live. Series counts use the Series.videos M2M (what link_series populates);
    topic counts use the reverse of Video.topic (what link_videos populates).
    """
    latest_videos = Video.objects.filter(is_livestream=False).order_by("-date_recorded")[:6]

    def featured_series():
        return [
            {
                "name": s.name,
                "summary": s.summary,
                "videosCount": s.videos_count,
                "url": s.get_absolute_url(),
            }
            for s in Series.objects.annotate(videos_count=Count("videos"))
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
            for t in Topic.objects.annotate(videos_count=Count("video"))
            .filter(videos_count__gt=0)
            .order_by("-videos_count")[:12]
        ]

    return render(
        request,
        "Welcome",
        {
            "livestreams": [],
            "latest_videos": video_card_props(latest_videos),
            # Below-the-fold sections load when scrolled into view (WhenVisible):
            # their queries don't run at all on first paint.
            "featured_series": optional(featured_series),
            "topics_data": optional(topics_data),
            "topics_total": optional(lambda: Topic.objects.count()),
        },
    )


def browse_all_livestreams(request):
    paginator = Paginator(Video.objects.filter(is_livestream=True).order_by("-date_recorded"), pagination_per_page)
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
            "title": "Past Live Streams",
            "description": f"Recordings of previous live services, most recent first "
            f"(page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def browse_all_latest(request):
    paginator = Paginator(Video.objects.filter(is_livestream=False).order_by("-date_recorded"), pagination_per_page)
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
            "title": "Latest Videos",
            "description": f"All videos, most recent first (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def search(request):
    searchquery = request.GET["search"]
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    video_results = []
    video_results += Video.objects.filter(name__icontains=searchquery)
    video_results += [v for v in Video.objects.filter(description__icontains=searchquery) if v not in video_results]
    paginator = Paginator(video_results, pagination_per_page)
    paginated = paginator.page(page_num)
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
            matches = matches.annotate(n=Count(count_relation))
            category_results += [
                {
                    "category": model_name,
                    "name": x.name,
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
            for x in Bible_Book.objects.filter(summary__icontains=searchquery).annotate(n=Count("video"))
        ]
        return render(
            request,
            "Search",
            {
                "title": f"Search for '{searchquery}'",
                "description": f"Found {len(video_results)} {'video' if len(video_results) == 1 else 'videos'} \
(page {page_num} of {paginator.num_pages})",
                "videos": video_card_props(paginated.object_list),
                "categories": category_results,
                "has_prev_page": paginated.has_previous(),
                "has_next_page": paginated.has_next(),
            },
        )
    else:
        return render(
            request,
            "Search",
            {
                "title": f"Search for '{searchquery}'",
                "description": f"Found {len(video_results)} {'video' if len(video_results) == 1 else 'videos'} \
(page {page_num} of {paginator.num_pages})",
                "videos": video_card_props(paginated.object_list),
                "has_prev_page": paginated.has_previous(),
                "has_next_page": paginated.has_next(),
            },
        )


def video(request, id):
    try:
        video_object = Video.objects.get(id=id)
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

        def up_next():
            # Series→video links live on the Series.videos M2M (no reverse
            # accessor from Video: related_name="+"), so filter by membership.
            series = Series.objects.filter(videos=video_object).first()
            if series is None:
                return None
            return {
                "series": {"name": series.name, "url": series.get_absolute_url()},
                "videos": video_card_props(series.videos.exclude(id=video_object.id).order_by("-date_recorded")[:6]),
            }

        return render(
            request,
            "WatchVideo",
            {
                "video": video_object,
                "video_metadata": video_metadata,
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

    try:
        bible_book = Bible_Book.objects.get(name=decoded_id)
    except Bible_Book.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Bible book not found: '{decoded_id}'",
                "description": f"Error retreiving Bible book data: '{e}'",
            },
        )

    paginator = Paginator(bible_book.video_set.all(), pagination_per_page)
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
            "title": f"Bible book: {bible_book.get_name_display()}",
            "description": f"{bible_book.summary} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
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

    paginator = Paginator(channel.video_set.all(), pagination_per_page)
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

    paginator = Paginator(demographic.video_set.all(), pagination_per_page)
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

    paginator = Paginator(ministry.video_set.all(), pagination_per_page)
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
        },
    )


def series_index(request):
    """All series as course-style cards: filterable, paginated, most-watched-in first."""
    query = request.GET.get("q", "").strip()
    series_qs = (
        Series.objects.annotate(videos_count=Count("videos"))
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
        },
    )


def topics_index(request):
    """All topics grouped under the legacy taxonomy's parent categories,
    headed by the three audiences (the old /demographic landing folded in)."""
    groups = {}
    for topic in Topic.objects.annotate(videos_count=Count("video")).order_by("name"):
        groups.setdefault(topic.category or "Other", []).append(
            {
                "name": topic.name,
                "videosCount": topic.videos_count,
                "url": topic.get_absolute_url(),
            }
        )

    audiences = [
        {
            "name": d.name,
            "videosCount": d.videos_count,
            "url": d.get_absolute_url(),
        }
        for d in Demographic.objects.annotate(videos_count=Count("video")).order_by("name")
    ]

    return render(
        request,
        "TopicsIndex",
        {
            "audiences": audiences,
            "topic_groups": [{"category": category, "topics": topics} for category, topics in sorted(groups.items())],
            "total": Topic.objects.count(),
        },
    )


def speakers_index(request):
    """Speaker directory: filterable, alphabetical, paginated."""
    query = request.GET.get("q", "").strip()
    speakers_qs = Speaker.objects.annotate(videos_count=Count("video")).filter(videos_count__gt=0).order_by("name")
    if query:
        speakers_qs = speakers_qs.filter(name__icontains=query)

    paginator = Paginator(speakers_qs, 48)
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)

    return render(
        request,
        "SpeakersIndex",
        {
            "speakers": [
                {
                    "name": s.name,
                    "videosCount": s.videos_count,
                    "url": s.get_absolute_url(),
                }
                for s in paginated.object_list
            ],
            "query": query,
            "total": paginator.count,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def books_index(request):
    """All 66 Bible books in canonical order, grouped by section."""
    groups = {}
    books = Bible_Book.objects.annotate(videos_count=Count("video"))
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
    ministries = [
        {
            "name": m.name,
            "summary": m.summary,
            "videosCount": m.videos_count,
            "url": m.get_absolute_url(),
        }
        for m in Ministry.objects.annotate(videos_count=Count("video")).filter(videos_count__gt=0).order_by("name")
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

    try:
        series = Series.objects.annotate(videos_count=Count("videos")).get(name=decoded_id)
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

    # Episodes live on the Series.videos M2M — the video_set FK reverse is
    # never populated, which is why this page used to show zero episodes.
    paginator = Paginator(series.videos.order_by("-date_recorded"), pagination_per_page)
    page_num = 1
    try:
        page_num = int(request.GET.get("page", 1))
    except ValueError:
        page_num = 1
    paginated = paginator.page(page_num)
    return render(
        request,
        "SeriesDetail",
        {
            "series_meta": {
                "name": series.name,
                "summary": series.summary,
                "videosCount": series.videos_count,
                "year_start": series.year_start,
                "year_end": series.year_end,
            },
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def browse_speaker(request, id):
    decoded_id = unquote(id)

    try:
        speaker = Speaker.objects.get(name=decoded_id)
    except Speaker.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": f"Speaker not found: '{decoded_id}'",
                "description": f"Error retreiving speaker data: '{e}'",
            },
        )

    paginator = Paginator(speaker.video_set.all(), pagination_per_page)
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
            "title": f"Speaker: {decoded_id}",
            "description": f"{speaker.bio} (page {page_num} of {paginator.num_pages})",
            "videos": video_card_props(paginated.object_list),
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
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

    paginator = Paginator(topic.video_set.all(), pagination_per_page)
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
            for b in Bible_Book.objects.annotate(videos_count=Count("video"))
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
            for c in Channel.objects.annotate(videos_count=Count("video"))
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
            for d in Demographic.objects.annotate(videos_count=Count("video"))
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
            for m in Ministry.objects.annotate(videos_count=Count("video")).prefetch_related("channel")
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
            for s in Speaker.objects.annotate(videos_count=Count("video"))
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
