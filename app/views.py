from inertia import render
import django
from catalogue.models.video import Video
from catalogue.models.bible_book import Bible_Book
from catalogue.models.channel import Channel
from catalogue.models.demograpic import (
    Demographic,
)  # FIXME Can we rename the file to fix spelling? Or does that break things?
from catalogue.models.ministry import Ministry
from catalogue.models.series import Series
from catalogue.models.speaker import Speaker
from catalogue.models.topic import Topic
from urllib.parse import unquote  # Import for URL decoding


def index(request):
    # Implementation of pagination will be needed in the future

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
    livestreams = Video.objects.filter(is_livestream=True).order_by("-date_created")
    return render(
        request,
        "Browse",
        {
            "videos": livestreams,
            "title": "Live Streams",
            "description": "All livestreamed content, most recent first",
        },
    )


def browse_all_latest(request):
    page = 1
    perpage = 24
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    try:
        latest_videos = Video.objects.filter(is_livestream=False).order_by(
            "-date_created"
        )[(page - 1) * perpage : page * perpage]
    except IndexError:
        latest_videos = []
    return render(
        request,
        "Browse",
        {
            "videos": latest_videos,
            "title": "Latest Videos",
            "description": "All videos, most recent first (page %s)" % page,
        },
    )


def search(request):
    searchquery = request.GET["search"]
    results = []
    results += Video.objects.filter(name__icontains=searchquery)
    results += [v for v in Video.objects.filter(description__icontains=searchquery) if v not in results]
    return render(
        request,
        "Search",
        {
            "results": results,
            "searchquery": searchquery,
        },
    )


def video(request, id):
    return render(
        request,
        "Video",
        {"video": Video.objects.get(id=id)},
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
                "title": "Bible book not found: '%s'" % decoded_id,
                "description": "Error retreiving Bible book data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": bible_book.video_set.all(),
            "title": "Bible book: %s" % bible_book.get_name_display(),
            "description": bible_book.summary,
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
                "title": "Channel not found: '%s'" % decoded_id,
                "description": "Error retreiving channel data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": channel.video_set.all(),
            "title": "Channel: %s" % decoded_id,
            "description": channel.summary,
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
                "title": "Demographic not found: '%s'" % decoded_id,
                "description": "Error retreiving demographic data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": demographic.video_set.all(),
            "title": "Demographic: %s" % decoded_id,
            "description": demographic.summary,
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
                "title": "Ministry not found: '%s'" % decoded_id,
                "description": "Error retreiving ministry data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": ministry.video_set.all(),
            "title": "Ministry: %s" % decoded_id,
            "description": ministry.summary,
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
                "title": "Series not found: '%s'" % decoded_id,
                "description": "Error retreiving series data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": series.video_set.all(),
            "title": "Series: %s" % decoded_id,
            "description": series.summary,
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
                "title": "Speaker not found: '%s'" % decoded_id,
                "description": "Error retreiving speaker data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": speaker.video_set.all(),
            "title": "Speaker: %s" % decoded_id,
            "description": speaker.bio,
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

    return render(
        request,
        "Browse",
        {
            "videos": topic.video_set.all(),
            "title": f"Topic: {decoded_id}",
            "description": topic.summary,
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
                "category": (
                    "Primary (Trusted)" if c.trusted else "Secondary (Untrusted)"
                ),
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
                    v.channel.name
                    for v in s.video_set.all()
                    if v.channel is not None and v.channel.name is not None
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
