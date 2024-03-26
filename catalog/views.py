from django.shortcuts import render
from django.views import generic


# Create your views here.
from .models import Video, Topic, Series, Speaker, Ministry, BibleBook, Demographic

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

def about(request):
    """View function for about page of site."""
    return render(request, 'about.html')

def donate(request):
    """View function for the donation page of site."""
    # NB will likely need to include either here or a seperate view 
    # functionality to make the donate button actually work.
    return render(request, 'donate.html')

def helppage(request):
    """
    View function for help page of site. 
    NB: called helppage instead of help to avoid overwriting a built in function.
    """
    return render(request, 'help.html')

def subscribe(request):
    """View function for subscribe page of site."""
    # as with donate, will need to figure out how to get the subscribe button to work.
    return render(request, 'subscribe.html')

def contact(request):
    """View function for contact page of site."""
    return render(request, 'contact.html')

def privacy(request):
    """View function for privacy policy page of site."""
    return render(request, 'privacy.html')