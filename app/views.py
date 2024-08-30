from inertia import render
import django
from django.core.paginator import Paginator
from catalogue.models.video import Video


def index(request):
    allVideos = Video.objects.all().order_by('-date_created')
    pageLimit = 6
    pageNumber = 1
    paginator = Paginator(allVideos, pageLimit)
    pageCount = paginator.num_pages
    totalCount = paginator.count
    currentPage = paginator.page(pageNumber)
    videos = currentPage.object_list
    nextPage = currentPage.next_page_number()

    return render(request, 'Welcome', {
        'videos': videos,
        'pagingMetadata': {
            'pageNumber': pageNumber,
            'nextPage': nextPage, 
            'pageCount': pageCount,
            'pageLimit': pageLimit,
            'totalCount': totalCount,
        }
    })
