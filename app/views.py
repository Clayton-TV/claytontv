from urllib.parse import unquote  # Import for URL decoding

from django.core.paginator import Paginator
from inertia import render

from catalogue.models.bible_book import Bible_Book
from catalogue.models.channel import Channel
from catalogue.models.demograpic import Demographic
from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from catalogue.models.video import Video

pagination_per_page = 24


def index(request):
    livestreams = Video.objects.filter(is_livestream=True).order_by("-date_created")[:10]
    latest_videos = Video.objects.filter(is_livestream=False).order_by("-date_created")[:10]
    topics_all = Topic.objects.all()

    topics_data = [
        {
            "category": t.category,
            "name": t.name,
            "videosCount": len(t.video_set.all()),
            "url": t.get_absolute_url(),
        }
        for t in topics_all
    ]

    series_data = [
        {
            "category": [m.name for m in s.ministry.all() if m.name is not None],
            "name": s.name,
            "videosCount": len(s.video_set.all()),
            "url": s.get_absolute_url(),
        }
        for s in Series.objects.all()
    ]

    return render(
        request,
        "Welcome",
        {
            "livestreams": livestreams,
            "latest_videos": latest_videos,
            "topics_data": topics_data,
            "series_data": series_data,
        },
    )


def browse_all_livestreams(request):
    paginator = Paginator(Video.objects.filter(is_livestream=True).order_by("-date_created"), pagination_per_page)
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
            "title": "Live Streams",
            "description": f"All livestreamed content, most recent first (page {page_num} of {paginator.num_pages})",
            "videos": paginated.object_list,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def browse_all_latest(request):
    paginator = Paginator(Video.objects.filter(is_livestream=False).order_by("-date_created"), pagination_per_page)
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
            "videos": paginated.object_list,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def search(request):
    searchquery = request.GET["search"]
    results = []
    results += Video.objects.filter(name__icontains=searchquery)
    results += [v for v in Video.objects.filter(description__icontains=searchquery) if v not in results]
    paginator = Paginator(results, pagination_per_page)
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
            "title": f"Search for '{searchquery}'",
            "description": f"Found {len(results)} {'result' if len(results) == 1 else 'results'}\
                            (page {page_num} of {paginator.num_pages})",
            "videos": paginated.object_list,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def video(request, id):
    try:
        video_object = Video.objects.get(id=id)
        video_metadata = {}
        # Properties to interrogate, with boolean for whether they are plural (True) or singular (False)
        props = {
            "topic": (video_object.topic, True),
            "channel": (video_object.channel, False),
            "series": (video_object.series, False),
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

        return render(
            request,
            "WatchVideo",
            {
                "video": video_object,
                "video_metadata": video_metadata,
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
            "videos": paginated.object_list,
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
            "videos": paginated.object_list,
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
            "videos": paginated.object_list,
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
            "videos": paginated.object_list,
            "has_prev_page": paginated.has_previous(),
            "has_next_page": paginated.has_next(),
        },
    )


def browse_series(request, id):
    decoded_id = unquote(id)

    try:
        series = Series.objects.get(name=decoded_id)
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

    paginator = Paginator(series.video_set.all(), pagination_per_page)
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
            "title": f"Series: {decoded_id}",
            "description": f"{series.summary} (page {page_num} of {paginator.num_pages})",
            "videos": paginated.object_list,
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
            "videos": paginated.object_list,
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
            "videos": paginated.object_list,
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
    retain_order = False

    if category == "book":
        categories_data = [
            {
                "category": b.type,
                "name": b.get_name_display(),
                "videosCount": len(b.video_set.all()),
                "url": b.get_absolute_url(),
            }
            for b in Bible_Book.objects.all()
        ]
        title = "Bible Books"
        description = "Browsing all Bible books"
        single_parent_category = True
        retain_order = True

    elif category == "channel":
        categories_data = [
            {
                "category": ("Primary (Trusted)" if c.trusted else "Secondary (Untrusted)"),
                "name": c.name,
                "videosCount": len(c.video_set.all()),
                "url": c.get_absolute_url(),
            }
            for c in Channel.objects.all()
        ]
        title = "Channels"
        description = "Browsing all known channels"
        single_parent_category = True
        retain_order = True

    elif category == "demographic":
        categories_data = [
            {
                "category": "All",
                "name": d.name,
                "videosCount": len(d.video_set.all()),
                "url": d.get_absolute_url(),
            }
            for d in Demographic.objects.all()
        ]
        title = "Demographic"
        description = "Browsing all known demographics"
        single_parent_category = True

    elif category == "ministry":
        categories_data = [
            {
                "category": [c.name for c in m.channel.all() if c.name is not None],
                "name": m.name,
                "videosCount": len(m.video_set.all()),
                "url": m.get_absolute_url(),
            }
            for m in Ministry.objects.all()
        ]
        title = "Ministries"
        description = "Browsing all known ministries"
        retain_order = True

    elif category == "series":
        categories_data = [
            {
                "category": [m.name for m in s.ministry.all() if m.name is not None],
                "name": s.name,
                "videosCount": len(s.video_set.all()),
                "url": s.get_absolute_url(),
            }
            for s in Series.objects.all()
        ]
        title = "Series"
        description = "Browsing all known series"
        retain_order = True

    elif category == "speaker":
        categories_data = [
            {
                "category": [
                    v.channel.name for v in s.video_set.all() if v.channel is not None and v.channel.name is not None
                ],
                "name": s.name,
                "videosCount": len(s.video_set.all()),
                "url": s.get_absolute_url(),
            }
            for s in Speaker.objects.all()
        ]
        title = "Speakers"
        description = "Browsing all known speakers"
        retain_order = True

    elif category == "topic":
        categories_data = [
            {
                "category": t.category,
                "name": t.name,
                "videosCount": len(t.video_set.all()),
                "url": t.get_absolute_url(),
            }
            for t in Topic.objects.all()
        ]
        title = "Topics"
        description = "Browsing all known topics"
        single_parent_category = True
        retain_order = True

    if categories_data is not None:
        return render(
            request,
            "CategoriesBrowsePage",
            {
                "categories_data": categories_data,
                "title": title,
                "description": description,
                "single_parent_category": single_parent_category,
                "retain_order": retain_order,
            },
        )
