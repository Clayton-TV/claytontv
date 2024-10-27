from django.urls import path

from . import views

app_name = "livestreams"

urlpatterns = [
    path("", views.index, name="index"),
]
