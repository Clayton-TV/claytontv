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

def video(request, id):
    return render(
        request,
        "Video",
        {
            "video": Video.objects.get(id=id)
        },
    )
