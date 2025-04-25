from inertia import render
import django
from catalogue.models.video import Video
from catalogue.models.bible_book import Bible_Book
from catalogue.models.channel import Channel
from catalogue.models.demograpic import Demographic # FIXME Can we rename the file to fix spelling? Or does that break things?
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

    return render(
        request,
        "Welcome",
        {
            "livestreams": livestreams,
            "latest_videos": latest_videos,
            "topics_data": topics_data,
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
    # Decode the URL-encoded `id` parameter
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
            "title": "Bible book: %s" % decoded_id,
            "description": bible_book.summary,
        },
    )

def browse_channel(request, id):
    # Decode the URL-encoded `id` parameter
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
    # Decode the URL-encoded `id` parameter
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
    # Decode the URL-encoded `id` parameter
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
    # Decode the URL-encoded `id` parameter
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
    # Decode the URL-encoded `id` parameter
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
    # Decode the URL-encoded `id` parameter
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
