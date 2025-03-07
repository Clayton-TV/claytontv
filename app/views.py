from inertia import render
import django
from catalogue.models.video import Video
from catalogue.models.topic import Topic


def index(request):
    # TODO: paginate

    livestreams = Video.objects.filter(is_livestream=True).order_by("-date_created")
    latest_videos = Video.objects.filter(is_livestream=False).order_by("-date_created")
    topics_all = Topic.objects.all()

    topics_data = [
        {"category": t.category, "name": t.name, "videosCount": len(t.videos.all())}
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
    results += [
        v
        for v in Video.objects.filter(description__icontains=searchquery)
        if not v in results
    ]
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
    try:
        topic = Topic.objects.get(name=id)
    except Topic.DoesNotExist as e:
        return render(
            request,
            "Browse",
            {
                "videos": [],
                "title": "Topic not found: '%s'" % id,
                "description": "Error retreiving topic data: '%s'" % e,
            },
        )

    return render(
        request,
        "Browse",
        {
            "videos": topic.video_set.all(),
            "title": "Topic: %s" % id,
            "description": topic.summary,
        },
    )