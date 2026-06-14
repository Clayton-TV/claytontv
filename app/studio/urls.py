"""Studio URLs, mounted under ``/studio/`` (see app/urls.py). Login is public;
everything else is gated by ``studio_required`` on the view."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.library, name="studio_library"),
    path("login", views.login_view, name="studio_login"),
    # Beta-only secret magic link (key-gated; 404 without the secret). See settings.
    path("dev-login", views.dev_login, name="studio_dev_login"),
    # Library mutations (all @studio_required + POST + CSRF).
    path("videos/bulk-status", views.bulk_status, name="studio_bulk_status"),
    path("videos/delete", views.delete_videos, name="studio_delete_videos"),
    path("videos/<str:id>/status", views.set_status, name="studio_set_status"),
]
