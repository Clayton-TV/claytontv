"""Studio URLs, mounted under ``/studio/`` (see app/urls.py). Login is public;
everything else is gated by ``studio_required`` on the view."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="studio_index"),
    path("login", views.login_view, name="studio_login"),
]
