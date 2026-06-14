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
