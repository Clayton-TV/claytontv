import os

from inertia import share

from catalogue.youtube_live import is_live_now

# from .models import User


class HandleInertiaRequests:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This is where you can add your custom logic before the view is called
        share(
            request,
            name=os.getenv("APP_NAME"),
            auth={
                "user": {
                    "id": request.user.id if request.user.is_authenticated else "123",
                    "name": request.user.get_full_name() if request.user.is_authenticated else "Test User",
                    "email": request.user.email if request.user.is_authenticated else "test@user.co",
                }
            },
            sidebarOpen=request.COOKIES.get("sidebar_state", "false") == "true",
            # Global flag for the "Live" nav indicator (one cheap exists()).
            # Skipped for JSON /api/ endpoints (e.g. the keystroke-hot palette)
            # which never render the nav, so they pay nothing for it.
            live_now=False if request.path.startswith("/api/") else is_live_now(),
        )

        response = self.get_response(request)

        # This is where you can add your custom logic after the view is called
        return response
