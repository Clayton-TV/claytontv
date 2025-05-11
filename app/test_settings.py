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
