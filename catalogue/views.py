from django.http import HttpResponse


def index(request):
    return HttpResponse("Catalogue.")


def show(request, video_id):
    return HttpResponse(f"Showing video {video_id}.")
