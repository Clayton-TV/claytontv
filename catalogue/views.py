from django.http import HttpResponse
from inertia import render
# NB: the string passed to the return argument for render requests
# should point to the file location for the .vue page within resources/js/Components/Pages


def index(request):
    return HttpResponse("Catalogue.")


def show(request, video_id):
    return HttpResponse(f"Showing video {video_id}.")

# search results pages

def quick_results(request):
    return render(request, 'Catalogue/quickbar_search_results')

# static pages

def about(request):
    return render(request, 'Catalogue/About')

def contact(request):
    return render(request, 'Catalogue/Contact')

def donate(request):
    return render(request, 'Catalogue/Donation')

def subscribe(request):
    return render(request, 'Catalogue/Subscribe')

def give(request):
    return render(request, 'Catalogue/GetInvolved/Give')

def updates(request):
    return render(request, 'Catalogue/GetInvolved/Updates')