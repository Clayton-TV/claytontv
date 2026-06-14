"""Studio views: the custom Inertia login and the (placeholder) gated index.

House style: thin views. Auth lives in ``app.auth``/``app.studio.auth``; these
just wire request → response.
"""

import secrets

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.http import Http404
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render, share

from app.auth import can_edit_content

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


@studio_required
def index(request):
    """``/studio`` — the gated Studio shell. Slices 2-3 fill it in."""
    return render(request, "Studio/Index", {})
