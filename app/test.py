import os

from .base import *  # noqa: F403
from .base import BASE_DIR

SECRET_KEY = os.environ.get("SECRET_KEY", "unit-test-key")

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
