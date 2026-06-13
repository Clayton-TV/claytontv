"""Rebuild the Typesense ``content`` search index from the database.

Run after the destructive importers (they delete-all-then-reload) and whenever
the index drifts. Safe to run repeatedly — it drops and recreates the
collection. No-op-safe: errors loudly if Typesense is unconfigured/unreachable.
"""

from django.core.management.base import BaseCommand, CommandError

from catalogue.search import COLLECTION, SearchUnavailableError, reindex


class Command(BaseCommand):
    help = "Rebuild the Typesense search index from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Documents per import request (default: 500).",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"Rebuilding the '{COLLECTION}' Typesense collection…")
        try:
            total = reindex(batch_size=options["batch_size"], log=self.stdout.write)
        except SearchUnavailableError as exc:
            raise CommandError(
                f"Typesense unavailable ({exc}). Set TYPESENSE_API_KEY/HOST and ensure the container is running."
            ) from exc
        self.stdout.write(self.style.SUCCESS(f"Indexed {total} documents into '{COLLECTION}'."))
