"""Guard for the legacy delete-all-then-reload CSV importers.

These commands wipe a table before reloading from CSV — they exist only to seed
a **local** dev database (SQLite). Epic 2 replaced ingestion on real databases
with idempotent upserts (`catalogue/ingest/`, `sync_live_admin`). This guard
stops anyone pointing the destructive importers at beta/prod (Postgres).

Underscore-prefixed so Django's command discovery ignores it (not a command).
"""

import os

from django.core.management.base import CommandError
from django.db import connection


def guard_destructive():
    """Raise unless it's safe to wipe-and-reload: a SQLite (local) database, or
    an explicit ``ALLOW_DESTRUCTIVE_IMPORT=1`` override for the rare deliberate case."""
    engine = connection.settings_dict.get("ENGINE", "")
    if "sqlite" in engine or os.getenv("ALLOW_DESTRUCTIVE_IMPORT") == "1":
        return
    raise CommandError(
        f"Refusing to run a destructive (delete-all-then-reload) importer against a "
        f"non-SQLite database ({engine or 'unknown'}). These are local-seed-only; on real "
        f"databases use the Epic 2 upsert importers (ingest_legacy_dump / sync_live_admin). "
        f"Set ALLOW_DESTRUCTIVE_IMPORT=1 if you genuinely intend to wipe this database."
    )
