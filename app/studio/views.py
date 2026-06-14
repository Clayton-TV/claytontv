"""Studio views: the custom Inertia login and the (placeholder) gated index.

House style: thin views. Auth lives in ``app.auth``/``app.studio.auth``; these
just wire request → response.
"""

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render, share

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


@studio_required
def index(request):
    """``/studio`` — the gated Studio shell. Slices 2-3 fill it in."""
    return render(request, "Studio/Index", {})
