from urllib.parse import unquote  # Import for URL decoding

from inertia import render

from catalogue.models.topic import Topic
from catalogue.models.video import Video


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
