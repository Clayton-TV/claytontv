import os

from .base import *  # noqa: F403

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ["claytontv.co.uk", "*.claytontv.co.uk"]

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        # ...
    },
}

# Logging
