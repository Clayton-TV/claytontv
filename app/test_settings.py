import os

from .base_settings import *  # noqa: F403
from .base_settings import TYPESENSE

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

# Search runs through the ORM fallback by default so the suite is deterministic
# regardless of a developer's environment (test data is never indexed). The
# guarded live search tests re-enable Typesense from the environment for their
# own test only.
TYPESENSE = {**TYPESENSE, "api_key": ""}
