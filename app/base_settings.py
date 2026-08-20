import os
from pathlib import Path

from django.conf.global_settings import MEDIA_ROOT, STATICFILES_DIRS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

is_debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django_vite",
    "inertia",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
    "app.studio.apps.StudioConfig",
    "catalogue.apps.CatalogueConfig",
    "livestreams.apps.LivestreamsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "inertia.middleware.InertiaMiddleware",
    "app.http.middleware.HandleInertiaRequests",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles_collected"

INERTIA_LAYOUT = "app.html"

# CSRF ↔ Inertia. Inertia's request client reads the ``XSRF-TOKEN`` cookie and
# echoes it as the ``X-XSRF-TOKEN`` header on every POST/PUT/PATCH/DELETE. Point
# Django's CSRF machinery at those names so Inertia submissions (the Studio
# login + mutations, Add-a-video) carry a valid token out of the box — otherwise
# Django looks for ``csrftoken``/``X-CSRFToken`` and rejects every Inertia POST
# with a 403. The cookie must stay JS-readable (HTTPONLY False, the default) so
# Inertia can read it; pair with ``@ensure_csrf_cookie`` on the pages that POST.
CSRF_COOKIE_NAME = "XSRF-TOKEN"
CSRF_HEADER_NAME = "HTTP_X_XSRF_TOKEN"
# Fail loud if a view passes a raw model/queryset as a prop (see the encoder
# docstring): the default encoder would recurse on our cyclic relations.
from app.inertia_encoder import StrictInertiaJsonEncoder  # noqa: E402

INERTIA_JSON_ENCODER = StrictInertiaJsonEncoder

DJANGO_VITE = {
    "default": {
        "dev_mode": is_debug,
        "dev_server_host": os.getenv("VITE_HOST", "localhost"),
        "dev_server_port": os.getenv("VITE_PORT", 5173),
        "static_url_prefix": "build" if not is_debug else "",
    }
}

STATICFILES_DIRS = [
    BASE_DIR / "public",  # For favicon, robots.txt, images/ etc.
]

MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Typesense search backend (catalogue/search.py). Optional everywhere: when
# unconfigured (no API key) or unreachable, the search views fall back to ORM
# icontains, so search never hard-fails. Dev and beta each run their own
# loopback-only container on their own port (prod is not provisioned yet — see
# docs/DEPLOYMENT.md); local dev uses docker-compose.yml. NOTE: the port default
# below is 8108, which is BETA's — every non-beta environment must set
# TYPESENSE_PORT explicitly, or its reindex will target beta's index.
TYPESENSE = {
    "api_key": os.getenv("TYPESENSE_API_KEY", ""),
    "host": os.getenv("TYPESENSE_HOST", "127.0.0.1"),
    "port": os.getenv("TYPESENSE_PORT", "8108"),
    "protocol": os.getenv("TYPESENSE_PROTOCOL", "http"),
    "connection_timeout_seconds": int(os.getenv("TYPESENSE_TIMEOUT", "2")),
}

# Ollama (self-hosted LLM) for AI content enrichment (Epic #201,
# catalogue/enrichment.py). The host is reachable over tailscale; defaults point
# at the verified host/model. Mirrors the TYPESENSE block: host + model are
# env-configurable, never hardcoded in logic. The enrichment client is
# best-effort — an unreachable host degrades to no-op, never an error.
OLLAMA = {
    "host": os.getenv("OLLAMA_HOST", "http://100.81.40.52:11434"),
    "model": os.getenv("OLLAMA_MODEL", "gemma4:31b-it-qat"),
    "timeout_seconds": int(os.getenv("OLLAMA_TIMEOUT", "120")),
}

# When True, AI-derived enrichment may surface as unlabelled public metadata
# (watch-page summary fallback + SEO meta). Default off: enrichment is invisible
# infrastructure (search recall) until consciously flipped (Epic #201, E4).
AI_ENRICHMENT_PUBLIC = os.getenv("AI_ENRICHMENT_PUBLIC", "false").lower() == "true"

# Studio dev login — BETA ONLY, NEVER set on production. A secret magic link:
# GET /studio/dev-login?key=<STUDIO_DEV_LOGIN_KEY> one-click-signs-in the single
# configured editor (STUDIO_DEV_LOGIN_USER) with NO credentials. The endpoint
# 404s unless the key is set AND matches (so it's invisible without the secret).
# Empty key (the default everywhere) = feature off. Remove at the prod cutover.
STUDIO_DEV_LOGIN_KEY = os.getenv("STUDIO_DEV_LOGIN_KEY", "")
STUDIO_DEV_LOGIN_USER = os.getenv("STUDIO_DEV_LOGIN_USER", "")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
