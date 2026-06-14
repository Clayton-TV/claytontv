import os

import dj_database_url
from django.conf.global_settings import CACHES, SESSION_ENGINE

from .base_settings import *  # noqa: F403

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Error tracking (self-hosted, sentry.tgo.dev). Activates only when a DSN is
# present in the environment, so local/CI runs are unaffected.
if os.getenv("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        environment=os.getenv("SENTRY_ENVIRONMENT", "beta"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
    )

# Django wildcard syntax is a leading dot (".example.com" matches subdomains);
# the previous "*.claytontv.co.uk" entry matched nothing.
ALLOWED_HOSTS = ["claytontv.test", "claytontv.co.uk", ".claytontv.co.uk"]

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
            # Pooled connections must be health-checked: a postgres restart
            # during the 2026-06-12 apt upgrade left every worker serving a
            # dead connection ("SSL connection has been closed unexpectedly").
            conn_health_checks=True,
        ),
    }

# Redis
if not os.getenv("REDIS_URL"):
    import logging

    logging.warning("REDIS_URL environment variable not set. Using local Redis instance which may not be available.")

# Django's BUILT-IN Redis backend — it forwards unknown OPTIONS to the redis
# client constructor, so the django-redis-only "CLIENT_CLASS" key raised
# `TypeError: AbstractConnection.__init__() got an unexpected keyword argument
# 'CLIENT_CLASS'` every time the pool opened a new connection (and a downstream
# `IndexError: pop from empty list`). django-redis isn't installed; the built-in
# backend needs no CLIENT_CLASS. Don't re-add it unless switching to django-redis.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Fix Vite manifest path
DJANGO_VITE["default"]["manifest_path"] = STATIC_ROOT / "build" / "manifest.json"  # noqa: F405
