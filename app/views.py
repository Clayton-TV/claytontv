from inertia import render
import django
from catalogue.models.video import Video


def index(request):
    # TODO: paginate
    # videos = Video.objects.all()
    # videos = videos.order_by('-date_created')

    livestreams = Video.objects.filter(is_livestream=True).order_by('-date_created')
    latest_videos = Video.objects.filter(is_livestream=False).order_by('-date_created')


    return render(request, 'Welcome', {
        'livestreams': livestreams,
        'latest_videos': latest_videos,
    })
