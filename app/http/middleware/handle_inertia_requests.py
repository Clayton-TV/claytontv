import os

from django.contrib.messages import get_messages
from inertia import share

from catalogue.youtube_live import is_live_now


def _auth_user(user):
    """Real signed-in user for Inertia, or None when anonymous. No placeholder —
    the frontend treats a null user as logged-out (real auth lands in Epic 3)."""
    if not user.is_authenticated:
        return None
    return {
        "id": user.id,
        "name": user.get_full_name() or user.get_username(),
        "email": user.email,
    }


class HandleInertiaRequests:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This is where you can add your custom logic before the view is called
        share(
            request,
            name=os.getenv("APP_NAME"),
            auth={"user": _auth_user(request.user)},
            sidebarOpen=request.COOKIES.get("sidebar_state", "false") == "true",
            # Global flag for the "Live" nav indicator (one cheap exists()).
            # Skipped for JSON /api/ endpoints (e.g. the keystroke-hot palette)
            # which never render the nav, so they pay nothing for it.
            live_now=False if request.path.startswith("/api/") else is_live_now(),
            # One-shot flash messages (Django messages → toast). Skipped for
            # /api/ so a keystroke-hot endpoint can't consume a pending message
            # before the page that should show it renders.
            flash=[]
            if request.path.startswith("/api/")
            else [{"level": m.level_tag, "message": str(m)} for m in get_messages(request)],
        )

        response = self.get_response(request)

        # This is where you can add your custom logic after the view is called
        return response
