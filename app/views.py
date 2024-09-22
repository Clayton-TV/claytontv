from inertia import render
import django
from django.core.paginator import Paginator
from catalogue.models.video import Video


def index(request):
    allVideos = Video.objects.all().order_by('-date_created')
    pageLimit = 10
    pageNumber = 1
    paginator = Paginator(allVideos, pageLimit)
    currentPage = paginator.page(pageNumber)
    videos = currentPage.object_list

    return render(request, 'Welcome', {
        'videos': videos,
    })
