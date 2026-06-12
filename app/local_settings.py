import os

from .base_settings import *  # noqa: F403
from .base_settings import BASE_DIR

SECRET_KEY = os.environ.get("SECRET_KEY")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]

# Server-side rendering: opt in by running the SSR server (npm run build-ssr && npm run ssr)
# and setting INERTIA_SSR_ENABLED=true in .env
INERTIA_SSR_ENABLED = os.getenv("INERTIA_SSR_ENABLED", "False").lower() in ("true", "1", "yes")
INERTIA_SSR_URL = os.getenv("INERTIA_SSR_URL", "http://127.0.0.1:13714")

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
