"""Studio views: the custom Inertia login and the gated Library (Slice 2).

House style: thin views. Auth lives in ``app.auth``/``app.studio.auth``; the
Library's data assembly and mutations live in ``app.studio.services``; these
just wire request → service → response.
"""

import json
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from inertia import render, share

from app.auth import can_edit_content
from catalogue.metadata import MetadataError, fetch_metadata
from catalogue.models.video import DRAFT, PUBLISHED

from . import services
from .auth import studio_required

# Only ever redirect to local paths after login — never an attacker-supplied
# absolute/off-site URL.
DEFAULT_REDIRECT = "/studio"


class _Payload:
    """Read POST fields from an Inertia request body.

    Inertia serialises a plain-object POST as a **JSON body** (Content-Type
    ``application/json``), so ``request.POST`` is empty for real browser
    submissions — only form-encoded posts (e.g. Django's test client) populate
    it. This normaliser reads either: JSON when that's what arrived, else
    ``request.POST``. ``get`` returns a scalar; ``getlist`` always a list, and
    accepts both ``key`` and ``key[]`` forms.
    """

    def __init__(self, request):
        content_type = (request.content_type or "").lower()
        if content_type.startswith("application/json"):
            try:
                self._json = json.loads(request.body or "{}")
            except (ValueError, TypeError):
                self._json = {}
        else:
            self._json = None
            self._post = request.POST

    def get(self, key, default=None):
        if self._json is not None:
            value = self._json.get(key, default)
            return value if value is not None else default
        return self._post.get(key, default)

    def getlist(self, key):
        if self._json is not None:
            value = self._json.get(key)
            if value is None:
                value = self._json.get(f"{key}[]")
            if value is None:
                return []
            return value if isinstance(value, list) else [value]
        return self._post.getlist(f"{key}[]") or self._post.getlist(key)


def _safe_next(request):
    nxt = _Payload(request).get("next") or request.GET.get("next") or ""
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return DEFAULT_REDIRECT


@ensure_csrf_cookie
def login_view(request):
    """``/studio/login``.

    GET renders the Inertia login page. ``ensure_csrf_cookie`` is load-bearing:
    it guarantees the XSRF cookie is set so Inertia's client echoes it back as
    the ``X-XSRF-TOKEN`` header on the POST (CSRF names aligned in settings).

    POST authenticates and logs in, then redirects to ``next`` (or ``/studio``).
    On bad credentials we share an error and re-render the page — inertia-django
    1.2 has no built-in error bag, so ``useForm().errors`` is fed via ``share``.
    """
    # Already signed in? Don't show the login form — go where they were headed.
    if request.user.is_authenticated:
        return redirect(_safe_next(request))

    if request.method == "POST":
        payload = _Payload(request)
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
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


@require_POST
def logout_view(request):
    """``POST /studio/logout`` — end the session and return to the login page.

    POST-only (a GET logout is CSRF-prone and lets a stray link sign editors
    out). The Studio "Sign out" button posts here via Inertia.
    """
    logout(request)
    return redirect("/studio/login")


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
@ensure_csrf_cookie
def library(request):
    """``/studio`` — the Library: every video (all statuses), filterable,
    searchable, paginated. The Studio's home base.

    ``ensure_csrf_cookie`` guarantees the XSRF cookie is present so the row/bulk
    mutations (Inertia POSTs) carry a valid CSRF token — including for a session
    that landed here straight from the magic link."""
    q, status, page = _library_filters(request)
    result = services.list_videos(search=q, status=status, page=page)
    return render(
        request,
        "Studio/Library",
        {
            "q": q,
            "status": status,
            "draft_count": services.draft_count(),
            **result,
        },
    )


@studio_required
@ensure_csrf_cookie
def review(request):
    """``/studio/review`` — the drafts triage queue. Approve (publish) / Edit /
    Reject (soft-delete) reuse the existing Library mutation endpoints."""
    try:
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    result = services.list_videos(status=DRAFT, page=page)
    return render(request, "Studio/Review", {**result})


def _back_to_library(request, payload=None):
    """Redirect back to the Library, preserving the editor's current filters so a
    mutation doesn't bounce them out of their search/status/page context. Inertia
    treats the redirect as a navigation and re-fetches the (now-updated) list."""
    nxt = (payload or _Payload(request)).get("next") or "/studio"
    if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("/studio")


def _posted_status(payload):
    """The ``status`` from a mutation body, or None if not a valid choice."""
    status = payload.get("status")
    return status if status in (DRAFT, PUBLISHED) else None


@studio_required
@require_POST
def set_status(request, id):
    """Publish/unpublish a single video. Saving re-fires the search signal."""
    payload = _Payload(request)
    status = _posted_status(payload)
    if status is None:
        messages.error(request, "Unknown status.")
        return _back_to_library(request, payload)
    if services.set_video_status(id, status):
        messages.success(request, "Published." if status == PUBLISHED else "Moved to drafts.")
    else:
        messages.error(request, "That video could not be found.")
    return _back_to_library(request, payload)


@studio_required
@require_POST
def bulk_status(request):
    """Publish/unpublish many videos at once."""
    payload = _Payload(request)
    status = _posted_status(payload)
    ids = payload.getlist("ids")
    if status is None or not ids:
        messages.error(request, "Nothing to update.")
        return _back_to_library(request, payload)
    count = services.set_videos_status(ids, status)
    verb = "Published" if status == PUBLISHED else "Moved to drafts"
    messages.success(request, f"{verb} {count} {'video' if count == 1 else 'videos'}.")
    return _back_to_library(request, payload)


@studio_required
@require_POST
def delete_videos(request):
    """Delete one or more videos. The post_delete signal drops them from search."""
    payload = _Payload(request)
    ids = payload.getlist("ids")
    if not ids:
        messages.error(request, "Nothing to delete.")
        return _back_to_library(request, payload)
    count = services.delete_videos(ids)
    messages.success(request, f"Deleted {count} {'video' if count == 1 else 'videos'}.")
    return _back_to_library(request, payload)


# --------------------------------------------------------------------------- #
# Add a video (paste-a-URL intake — Slice 3)
# --------------------------------------------------------------------------- #


@studio_required
@ensure_csrf_cookie
def add_video(request):
    """``/studio/add`` — the paste-a-URL intake form, with the classification
    choices the editor picks from. ``ensure_csrf_cookie`` guarantees the XSRF
    cookie is set so the page's fetch() metadata call can echo it."""
    return render(request, "Studio/AddVideo", {"taxonomy": services.taxonomy_options()})


@studio_required
@require_POST
def fetch_metadata_api(request):
    """``POST /studio/api/fetch-metadata`` {url} → JSON metadata preview.

    A plain JSON endpoint (not Inertia) the Add page calls as the editor pastes:
    returns ``{ok: true, metadata: {...}}``, or ``{ok: false, error}`` for an
    unsupported/failed URL, plus ``duplicate`` when the URL is already in the
    library so the form can warn before they fill anything in.
    """
    try:
        url = (json.loads(request.body or "{}").get("url") or "").strip()
    except (ValueError, TypeError):
        url = ""

    try:
        metadata = fetch_metadata(url)
    except MetadataError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=200)

    return JsonResponse({"ok": True, "metadata": metadata, "duplicate": services.find_duplicate(metadata["url"])})


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@studio_required
@require_POST
def create_video(request):
    """``POST /studio/videos/create`` — create a Studio video from the Add form.

    On a duplicate URL we keep the editor on the form with an inline error (their
    typed-in form state survives via Inertia's ``useForm``); on success we land
    them in the Library with a flash so they can see the new row."""
    post = _Payload(request)
    try:
        video = services.create_video(
            url=post.get("url", ""),
            name=post.get("name", ""),
            description=post.get("description", ""),
            thumbnail=post.get("thumbnail") or None,
            duration_seconds=_int_or_none(post.get("duration_seconds")),
            date_recorded=post.get("date_recorded") or None,
            status=post.get("status", DRAFT),
            speaker_ids=post.getlist("speaker_ids"),
            topic_ids=post.getlist("topic_ids"),
            bible_book_ids=post.getlist("bible_book_ids"),
            demographic_ids=post.getlist("demographic_ids"),
            ministry_ids=post.getlist("ministry_ids"),
            series_id=post.get("series_id") or None,
        )
    except services.DuplicateVideoError as exc:
        share(request, errors={"url": f"“{exc.video.name}” is already in the library."})
        return render(request, "Studio/AddVideo", {"taxonomy": services.taxonomy_options()})

    verb = "Published" if video.status == PUBLISHED else "Saved as draft"
    messages.success(request, f"{verb}: “{video.name}”.")
    return redirect("/studio")


# --------------------------------------------------------------------------- #
# Edit a video (Slice 4a)
# --------------------------------------------------------------------------- #


@studio_required
@ensure_csrf_cookie
def edit_video(request, id):
    """``/studio/videos/<id>/edit`` — the full tabbed editor for one video."""
    video = services.get_video_for_edit(id)
    if video is None:
        raise Http404
    return render(request, "Studio/EditVideo", {"video": video, "taxonomy": services.taxonomy_options()})


@studio_required
@require_POST
def update_video(request, id):
    """``POST /studio/videos/<id>/update`` — save edits (status-neutral; publish
    is a separate action). On a URL clash, re-render the editor with an inline
    error (the form's typed state survives via Inertia)."""
    post = _Payload(request)
    try:
        ok = services.update_video(
            id,
            name=post.get("name", ""),
            description=post.get("description", ""),
            url=post.get("url", ""),
            thumbnail=post.get("thumbnail") or None,
            duration_seconds=_int_or_none(post.get("duration_seconds")),
            date_recorded=post.get("date_recorded") or None,
            is_livestream=bool(post.get("is_livestream")),
            number_in_series=_int_or_none(post.get("number_in_series")),
            speaker_ids=post.getlist("speaker_ids"),
            topic_ids=post.getlist("topic_ids"),
            bible_book_ids=post.getlist("bible_book_ids"),
            demographic_ids=post.getlist("demographic_ids"),
            ministry_ids=post.getlist("ministry_ids"),
            series_id=post.get("series_id") or None,
            alternate_urls=post.get("alternate_urls") or [],
            related_resources=post.get("related_resources") or [],
        )
    except services.DuplicateVideoError as exc:
        share(request, errors={"url": f"“{exc.video.name}” already uses that link."})
        props = {"video": services.get_video_for_edit(id), "taxonomy": services.taxonomy_options()}
        return render(request, "Studio/EditVideo", props)
    if not ok:
        raise Http404
    messages.success(request, "Saved.")
    return redirect("/studio")
