"""Guards against settings misconfigurations that have bitten us in production."""

import importlib


def test_production_redis_cache_has_no_django_redis_only_options():
    # The built-in RedisCache forwards unknown OPTIONS to the redis client, so a
    # django-redis-only "CLIENT_CLASS" raised TypeError on every new connection
    # (and a downstream "pop from empty list" IndexError). django-redis isn't a
    # dependency — keep CLIENT_CLASS out of the built-in backend's OPTIONS.
    prod = importlib.import_module("app.production_settings")
    cache = prod.CACHES["default"]

    assert cache["BACKEND"] == "django.core.cache.backends.redis.RedisCache"
    assert "CLIENT_CLASS" not in cache.get("OPTIONS", {})


def test_a_malformed_retry_override_degrades_the_sync_instead_of_the_site():
    # LEGACY_ADMIN_RETRY_WAITS is an operator dial in shared/.env, which
    # wsgi.py loads BEFORE settings — so a typo'd value parsed eagerly would
    # stop every gunicorn worker booting. A bad value must cost the legacy
    # sync some patience, nothing else.
    base = importlib.import_module("app.base_settings")

    assert base.parse_retry_waits("5,15,60") == (5.0, 15.0, 60.0)
    assert base.parse_retry_waits("") == ()
    assert base.parse_retry_waits("2, five") == base.DEFAULT_RETRY_WAITS
    assert base.parse_retry_waits("2;5") == base.DEFAULT_RETRY_WAITS
