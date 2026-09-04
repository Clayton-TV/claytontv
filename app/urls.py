"""URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from app.legacy_redirects import legacy_video_redirect

from .views import (
    audiences_index,
    books_index,
    browse_all_latest,
    browse_all_livestreams,
    browse_bible_book,
    browse_categories,
    browse_channel,
    browse_demographic,
    browse_faceted,
    browse_ministry,
    browse_series,
    browse_speaker,
    browse_topic,
    index,
    ministries_index,
    palette,
    search,
    series_index,
    speakers_index,
    subscribe,
    topics_index,
    video,
    video_next,
)

urlpatterns = [
    path("", index, name="home"),
    # Studio (Epic 3): gated editorial area. Mounted before the public catalogue
    # routes so the /studio prefix is never shadowed by a public page.
    path("studio/", include("app.studio.urls")),
    path("livestreams/", browse_all_livestreams, name="browse_all_livestreams"),
    path("latest/", browse_all_latest, name="browse_all_latest"),
    path("admin/", admin.site.urls),
    path("search", search, name="search"),
    path("subscribe/", subscribe, name="subscribe"),
    path("browse/", browse_faceted, name="browse_faceted"),
    path("api/palette", palette, name="palette"),
    path("api/video/<int:id>/next", video_next, name="video_next"),
    path("video/<int:id>", video, name="video"),
    # Legacy clayton.tv watch URLs (…/0i0/<id>/) → 301 to /video/<id>, for cutover.
    re_path(
        r"^(?:new|find|schedule)/.*?0i0/(?P<pid>\d+)/?$",
        legacy_video_redirect,
        name="legacy_video_redirect",
    ),
    path("book/<str:id>", browse_bible_book, name="browse_bible_book"),
    path("channel/<str:id>", browse_channel, name="browse_channel"),
    path("audience/", audiences_index, name="audiences_index"),
    path("audience/<str:id>", browse_demographic, name="browse_audience"),
    path("demographic/<str:id>", browse_demographic, name="browse_demographic"),  # legacy links
    path("ministry/<str:id>", browse_ministry, name="browse_ministry"),
    path("series/<str:id>", browse_series, name="browse_series"),
    path("speaker/<str:id>", browse_speaker, name="browse_speaker"),
    path("topic/<str:id>", browse_topic, name="browse_topic"),
    path("book/", books_index, name="browse_categories_book"),
    path("channel/", browse_categories, name="browse_categories_channel"),
    # Audiences live on the Topics page now; the standalone landing is gone
    path("demographic/", RedirectView.as_view(url="/audience/"), name="browse_categories_demographic"),
    path("ministry/", ministries_index, name="browse_categories_ministry"),
    path("series/", series_index, name="browse_categories_series"),
    path("speaker/", speakers_index, name="browse_categories_speaker"),
    path("topic/", topics_index, name="browse_categories_topic"),
]
