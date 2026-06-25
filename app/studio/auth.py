"""Studio access gate. One decorator, applied to every Studio view, so the whole
``/studio`` prefix shares a single authorisation rule."""

from functools import wraps
from urllib.parse import urlencode

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from app.auth import can_edit_content


def studio_required(view):
    """Gate a Studio view.

    - Anonymous → redirect to ``/studio/login?next=<path>`` so they can sign in
      and bounce back to where they were headed.
    - Authenticated but not an editor → 403 (they have an account but no Studio
      access; sending them to login would just loop).
    - Editor or staff → allowed (reuses ``can_edit_content`` so the gate and the
      watch-page draft preview stay in lockstep).
    """

    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/studio/login?{urlencode({'next': request.get_full_path()})}")
        if not can_edit_content(request.user):
            return HttpResponseForbidden("You don't have access to the Studio.")
        return view(request, *args, **kwargs)

    return wrapped
