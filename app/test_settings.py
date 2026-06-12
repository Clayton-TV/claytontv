import os

from .base_settings import *  # noqa: F403

SECRET_KEY = os.environ.get("SECRET_KEY", "unit-test-key")

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# Vite dev mode emits plain script URLs instead of reading a build manifest,
# so tests never depend on a frontend build having run.
DJANGO_VITE = {
    "default": {
        "dev_mode": True,
    },
}
