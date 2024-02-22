from django.shortcuts import render

# Create your views here.
from .models import Video, Topic, Series, Speaker

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
