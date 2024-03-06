from django.shortcuts import render
from django.views import generic


# Create your views here.
from .models import Video, Topic, Series, Speaker, Ministry

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_videos = Video.objects.all().count()
    num_series = Series.objects.all().count()

    context = {
        'num_videos': num_videos,
        'num_series': num_series,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class VideoListView(generic.ListView):
    model = Video
    
class SeriesListView(generic.ListView):
    model = Series
    
class VideoDetailView(generic.DetailView):
    model = Video
    
class SeriesDetailView(generic.DetailView):
    model = Series