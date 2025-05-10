import os

from .base import *  # noqa: F403

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS = ["claytontv.test", "claytontv.co.uk", "*.claytontv.co.uk"]

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        # ...
    },
}

# Logging
