"""Studio URLs, mounted under ``/studio/`` (see app/urls.py). Login is public;
everything else is gated by ``studio_required`` on the view."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.library, name="studio_library"),
    path("review", views.review, name="studio_review"),
    path("add", views.add_video, name="studio_add_video"),
    path("bulk", views.bulk_add, name="studio_bulk_add"),
    path("login", views.login_view, name="studio_login"),
    path("logout", views.logout_view, name="studio_logout"),
    # Beta-only secret magic link (key-gated; 404 without the secret). See settings.
    path("dev-login", views.dev_login, name="studio_dev_login"),
    # JSON metadata preview for the Add form (not Inertia).
    path("api/fetch-metadata", views.fetch_metadata_api, name="studio_fetch_metadata"),
    path("api/bulk-create", views.bulk_create_api, name="studio_bulk_create"),
    # Editor (Slice 4a).
    path("videos/<str:id>/edit", views.edit_video, name="studio_edit_video"),
    path("videos/<str:id>/update", views.update_video, name="studio_update_video"),
    path("videos/<str:id>/suggest", views.suggest_video, name="studio_suggest_video"),
    # Library mutations (all @studio_required + POST + CSRF).
    path("videos/create", views.create_video, name="studio_create_video"),
    path("videos/bulk-status", views.bulk_status, name="studio_bulk_status"),
    path("videos/delete", views.delete_videos, name="studio_delete_videos"),
    path("videos/<str:id>/status", views.set_status, name="studio_set_status"),
]
