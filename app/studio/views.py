"""Studio views: the custom Inertia login and the gated Library (Slice 2).

House style: thin views. Auth lives in ``app.auth``/``app.studio.auth``; the
Library's data assembly and mutations live in ``app.studio.services``; these
just wire request → service → response.
"""

import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.http import Http404
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from inertia import render, share

from app.auth import can_edit_content
from catalogue.models.video import DRAFT, PUBLISHED

from . import services
from .auth import studio_required

# Only ever redirect to local paths after login — never an attacker-supplied
# absolute/off-site URL.
DEFAULT_REDIRECT = "/studio"


def _safe_next(request):
    nxt = request.POST.get("next") or request.GET.get("next") or ""
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return DEFAULT_REDIRECT


@ensure_csrf_cookie
def login_view(request):
    """``/studio/login``.

    GET renders the Inertia login page. ``ensure_csrf_cookie`` is load-bearing:
    it guarantees the ``csrftoken`` cookie is set so Inertia's axios echoes it
    back as ``X-CSRFToken`` on the POST (inertia-django POSTs rely on this).

    POST authenticates and logs in, then redirects to ``next`` (or ``/studio``).
    On bad credentials we share an error and re-render the page — inertia-django
    1.2 has no built-in error bag, so ``useForm().errors`` is fed via ``share``.
    """
    # Already signed in? Don't show the login form — go where they were headed.
    if request.user.is_authenticated:
        return redirect(_safe_next(request))

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Manual error-bag shim until inertia-django ships one (issue #49):
            # share(errors=...) merges into the shared props, and Inertia's
            # useForm exposes them as `errors` on the re-rendered page.
            share(request, errors={"detail": "That username or password wasn't right."})
            return _render_login(request)
        login(request, user)
        return redirect(_safe_next(request))

    return _render_login(request)


def _render_login(request):
    return render(request, "Studio/Login", {"next": _safe_next(request)})


def dev_login(request):
    """``/studio/dev-login?key=<secret>`` — BETA-ONLY secret magic link, NO
    credentials. Signs in the single configured editor (``STUDIO_DEV_LOGIN_USER``).

    Gated by a secret: 404 unless ``STUDIO_DEV_LOGIN_KEY`` is set AND the ``key``
    query param matches it (constant-time) — so the endpoint is invisible without
    the secret, even on beta. Only signs in an account that is actually an editor.
    The key is set in beta's .env ONLY; NEVER set it on production. Remove at cutover.
    """
    key = getattr(settings, "STUDIO_DEV_LOGIN_KEY", "")
    if not key or not secrets.compare_digest(request.GET.get("key", ""), key):
        raise Http404
    username = getattr(settings, "STUDIO_DEV_LOGIN_USER", "")
    user = get_user_model().objects.filter(username=username).first()
    if user is None or not can_edit_content(user):
        raise Http404
    # No password involved — set the session directly (the account may not even
    # have a usable password yet). Specify the backend since we skip authenticate().
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(DEFAULT_REDIRECT)


# --------------------------------------------------------------------------- #
# Library (the editor content list)
# --------------------------------------------------------------------------- #


def _library_filters(request):
    """The current ``(q, status, page)`` filters from a GET request."""
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", services.STATUS_ALL)
    if status not in services.STATUS_CHOICES:
        status = services.STATUS_ALL
    try:
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    return q, status, page


@studio_required
def library(request):
    """``/studio`` — the Library: every video (all statuses), filterable,
    searchable, paginated. The Studio's home base."""
    q, status, page = _library_filters(request)
    result = services.list_videos(search=q, status=status, page=page)
    return render(
        request,
        "Studio/Library",
        {
            "q": q,
            "status": status,
            **result,
        },
    )


def _back_to_library(request):
    """Redirect back to the Library, preserving the editor's current filters so a
    mutation doesn't bounce them out of their search/status/page context. Inertia
    treats the redirect as a navigation and re-fetches the (now-updated) list."""
    nxt = request.POST.get("next") or "/studio"
    if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("/studio")


def _posted_status(request):
    """The ``status`` from a mutation body, or None if not a valid choice."""
    status = request.POST.get("status")
    return status if status in (DRAFT, PUBLISHED) else None


@studio_required
@require_POST
def set_status(request, id):
    """Publish/unpublish a single video. Saving re-fires the search signal."""
    status = _posted_status(request)
    if status is None:
        messages.error(request, "Unknown status.")
        return _back_to_library(request)
    if services.set_video_status(id, status):
        messages.success(request, "Published." if status == PUBLISHED else "Moved to drafts.")
    else:
        messages.error(request, "That video could not be found.")
    return _back_to_library(request)


@studio_required
@require_POST
def bulk_status(request):
    """Publish/unpublish many videos at once."""
    status = _posted_status(request)
    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    if status is None or not ids:
        messages.error(request, "Nothing to update.")
        return _back_to_library(request)
    count = services.set_videos_status(ids, status)
    verb = "Published" if status == PUBLISHED else "Moved to drafts"
    messages.success(request, f"{verb} {count} {'video' if count == 1 else 'videos'}.")
    return _back_to_library(request)


@studio_required
@require_POST
def delete_videos(request):
    """Delete one or more videos. The post_delete signal drops them from search."""
    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    if not ids:
        messages.error(request, "Nothing to delete.")
        return _back_to_library(request)
    count = services.delete_videos(ids)
    messages.success(request, f"Deleted {count} {'video' if count == 1 else 'videos'}.")
    return _back_to_library(request)
