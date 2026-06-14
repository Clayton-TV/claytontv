"""Studio URLs, mounted under ``/studio/`` (see app/urls.py). Login is public;
everything else is gated by ``studio_required`` on the view."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="studio_index"),
    path("login", views.login_view, name="studio_login"),
    # Beta-only secret magic link (key-gated; 404 without the secret). See settings.
    path("dev-login", views.dev_login, name="studio_dev_login"),
]
