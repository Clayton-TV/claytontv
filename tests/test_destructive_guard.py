"""The destructive-importer guard (#286): the delete-all-then-reload CSV
importers must refuse to run against a non-SQLite (i.e. beta/prod) database."""

import pytest
from django.core.management.base import CommandError
from django.db import connection

from catalogue.management.commands._destructive import guard_destructive

pytestmark = pytest.mark.django_db


def test_guard_allows_sqlite():
    # The test database is SQLite — the guard should pass silently.
    guard_destructive()


def test_guard_blocks_non_sqlite(monkeypatch):
    monkeypatch.setitem(connection.settings_dict, "ENGINE", "django.db.backends.postgresql")
    with pytest.raises(CommandError):
        guard_destructive()


def test_guard_env_override(monkeypatch):
    monkeypatch.setitem(connection.settings_dict, "ENGINE", "django.db.backends.postgresql")
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_IMPORT", "1")
    guard_destructive()  # explicit override → no raise
