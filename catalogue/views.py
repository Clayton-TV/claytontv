from django.core.files.storage import storages
from inertia import render


def index(request):
    return render(request, "CatalogueIndex", {
        "videos": [
            {
                "title": "Video 1",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 2",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 3",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 4",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 5",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 6",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
            {
                "title": "Video 7",
                "datetime": "10:30am Monday 6th June 2025",
                "thumbnailUrl": "/static/images/sample-background.jpg"
            },
        ],
    })
