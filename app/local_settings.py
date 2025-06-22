import os

from .base_settings import *  # noqa: F403
from .base_settings import BASE_DIR, INSTALLED_APPS

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-u166q)-sn5ghr5qc7qvkp#1b6594lx!#y$y=%z1$iipepp0@gs")

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]

# Add development-only apps
INSTALLED_APPS += [
    "django_seed",
]

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
