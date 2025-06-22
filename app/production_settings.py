import os

import dj_database_url
from django.conf.global_settings import CACHES, SESSION_ENGINE

from .base_settings import *  # noqa: F403

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["claytontv.test", "claytontv.co.uk", "*.claytontv.co.uk"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Database
# Add a warning if DATABASE_URL is not set
if not os.getenv("DATABASE_URL"):
    import logging

    logging.warning(
        "DATABASE_URL environment variable not set. "
        "Please set this to a valid database URL or the application may not function correctly."
    )
    # Provide a fallback to prevent crashes during deployment
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
        ),
    }

# Redis
if not os.getenv("REDIS_URL"):
    import logging

    logging.warning(
        "REDIS_URL environment variable not set. "
        "Using local Redis instance which may not be available."
    )

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Fix Vite manifest path
DJANGO_VITE["default"]["manifest_path"] = os.path.join(
    STATIC_ROOT, "build", "manifest.json"
)  # noqa: F405
