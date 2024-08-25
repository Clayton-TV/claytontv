from inertia import render
import django
from catalogue.models.video import Video


def index(request):
    # TODO: paginate
    videos = Video.objects.all()

    return render(request, 'Welcome', {
        'videos': videos,
    })
