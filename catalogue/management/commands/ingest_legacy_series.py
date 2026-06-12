"""Idempotent import of the legacy series hierarchy — safe on a populated
database. Run after ingest_legacy_dump so programmes exist to link."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalogue.ingest.series_tree import ingest_series_trees


class Command(BaseCommand):
    help = "Upsert series, memberships, episode numbers and livestream flags from series.json"

    def add_arguments(self, parser):
        parser.add_argument("--series", required=True, help="Path to series.json")

    def handle(self, *args, **options):
        path = Path(options["series"])
        if not path.exists():
            raise CommandError(f"No such file: {path}")

        trees = json.loads(path.read_text())
        stats = ingest_series_trees(trees)
        self.stdout.write(
            self.style.SUCCESS(
                f"Series: {stats['series_created']} created, {stats['series_updated']} updated; "
                f"{stats['memberships']} memberships; livestream flags: +{stats['live_flagged']} "
                f"promoted, -{stats['live_demoted']} demoted."
            )
        )
