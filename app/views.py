from inertia import render
import django
from catalogue.models.video import Video


def index(request):
    # TODO: paginate

    livestreams = Video.objects.filter(is_livestream=True).order_by("-date_created")
    latest_videos = Video.objects.filter(is_livestream=False).order_by("-date_created")

    return render(
        request,
        "Welcome",
        {
            "livestreams": livestreams,
            "latest_videos": latest_videos,
        },
    )


def search(request):
    searchquery = request.GET["search"]
    results = []
    results += Video.objects.filter(name__icontains=searchquery)
    results += [v for v in Video.objects.filter(description__icontains=searchquery) if not v in results]
    return render(
        request,
        "Search",
        {
            "results": results,
            "searchquery": searchquery,
        },
    )
