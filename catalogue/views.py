from inertia import render
from django.http import HttpResponse
from catalogue.models.video import Video

def index(request):
    return render(request, 'Catalogue', { 'videos': Video.objects.all().order_by('-date_created') })

def show(request, video_id):
    return HttpResponse("Showing video {video_id}.")
