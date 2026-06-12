"""Production settings are env-driven; import the module fresh per scenario."""

import importlib
import sys

import sentry_sdk


def reload_production_settings(monkeypatch, **env):
    for key in ("SENTRY_DSN", "SENTRY_ENVIRONMENT", "DATABASE_URL", "REDIS_URL"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop("app.production_settings", None)
    return importlib.import_module("app.production_settings")


def test_pooled_connections_are_health_checked(monkeypatch):
    """A postgres restart once left every worker serving a dead pooled
    connection (500s until manual restart); health checks make that self-heal."""
    settings = reload_production_settings(monkeypatch, DATABASE_URL="postgres://u:p@localhost:5432/db")

    db = settings.DATABASES["default"]
    assert db["CONN_HEALTH_CHECKS"] is True
    assert db["CONN_MAX_AGE"] == 600


def test_sentry_initializes_only_when_dsn_is_set(monkeypatch):
    calls = []
    monkeypatch.setattr(sentry_sdk, "init", lambda **kwargs: calls.append(kwargs))

    reload_production_settings(monkeypatch)
    assert calls == []

    reload_production_settings(monkeypatch, SENTRY_DSN="https://key@sentry.tgo.dev/1")
    assert len(calls) == 1
    assert calls[0]["dsn"] == "https://key@sentry.tgo.dev/1"
    assert calls[0]["send_default_pii"] is False
