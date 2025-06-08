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
from django.urls import include, path

from .views import (
    index,
    search,
    video,
    browse_bible_book,
    browse_channel,
    browse_demographic,
    browse_ministry,
    browse_series,
    browse_speaker,
    browse_topic,
    browse_categories,
    browse_all_livestreams,
    browse_all_latest,
)

urlpatterns = [
    path("", index, name="home"),
    path("catalogue/", include("catalogue.urls"), name="catalogue"),
    path("livestreams/", browse_all_livestreams, name="browse_all_livestreams"),
    path("latest/", browse_all_latest, name="browse_all_latest"),
    path("admin/", admin.site.urls),
    path("search", search, name="search"),
    path("video/<int:id>", video, name="video"),
    path("book/<str:id>", browse_bible_book, name="browse_bible_book"),
    path("channel/<str:id>", browse_channel, name="browse_channel"),
    path("demographic/<str:id>", browse_demographic, name="browse_demographic"),
    path("ministry/<str:id>", browse_ministry, name="browse_ministry"),
    path("series/<str:id>", browse_series, name="browse_series"),
    path("speaker/<str:id>", browse_speaker, name="browse_speaker"),
    path("topic/<str:id>", browse_topic, name="browse_topic"),
    path("book/", browse_categories, name="browse_categories_book"),
    path("channel/", browse_categories, name="browse_categories_channel"),
    path("demographic/", browse_categories, name="browse_categories_demographic"),
    path("ministry/", browse_categories, name="browse_categories_ministry"),
    path("series/", browse_categories, name="browse_categories_series"),
    path("speaker/", browse_categories, name="browse_categories_speaker"),
    path("topic/", browse_categories, name="browse_categories_topic"),
]
