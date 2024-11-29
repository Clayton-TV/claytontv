from inertia import render
import django
from catalogue.models.video import Video
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie
import json

@ensure_csrf_cookie
def index(request):
    livestreams_paginator = Paginator(Video.objects.filter(is_livestream=True).order_by("-date_created"), 5)
    latest_videos_paginator = Paginator(Video.objects.filter(is_livestream=False).order_by("-date_created"), 5)
    pagenum_livestreams = 1
    pagenum_latestvids = 1
    if request.method == "POST" :
        postdata = json.loads(request.body)
        if "page" in postdata :
            if "id" in postdata :
                if postdata["id"] == "livestreams" :
                    pagenum_livestreams = postdata["page"]
                elif postdata["id"] == "latestvids" :
                    pagenum_latestvids = postdata["page"]

    return render(
        request,
        "Welcome",
        {
            "livestreams": livestreams_paginator.page(pagenum_livestreams).object_list,
            "latest_videos": latest_videos_paginator.page(pagenum_latestvids).object_list,
            "pagenum_livestreams": pagenum_livestreams,
            "pagenum_latestvids": pagenum_latestvids,
            "num_pages_livestreams": livestreams_paginator.num_pages,
            "num_pages_latestvids": latest_videos_paginator.num_pages,
        },
    )


def search(request):
    searchquery = request.GET["search"]
    results = []
    results += Video.objects.filter(name__icontains=searchquery)
    results += [
        v
        for v in Video.objects.filter(description__icontains=searchquery)
        if not v in results
    ]
    return render(
        request,
        "Search",
        {
            "results": results,
            "searchquery": searchquery,
        },
    )


def video(request, id):
    return render(
        request,
        "Video",
        {"video": Video.objects.get(id=id)},
    )
