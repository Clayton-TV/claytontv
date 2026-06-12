"""Idempotent import of the legacy programme dump — safe on a populated
database (upserts only, no deletes of videos). Supersedes the CSV chain."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalogue.ingest.legacy import ingest_programmes


class Command(BaseCommand):
    help = "Upsert videos and their links from a legacy programmes.json dump"

    def add_arguments(self, parser):
        parser.add_argument("--programmes", required=True, help="Path to programmes.json")

    def handle(self, *args, **options):
        path = Path(options["programmes"])
        if not path.exists():
            raise CommandError(f"No such file: {path}")

        programmes = json.loads(path.read_text())
        if not isinstance(programmes, list):
            programmes = next(iter(programmes.values()))

        stats = ingest_programmes(programmes)
        self.stdout.write(
            self.style.SUCCESS(
                f"Ingested {len(programmes)} programmes: "
                f"{stats['created']} created, {stats['updated']} updated, "
                f"{stats['skipped_no_media']} skipped (no playable media), "
                f"{stats['skipped_url_collision']} skipped (duplicate URL — needs dedup review)."
            )
        )
        for collision in stats["url_collisions"]:
            self.stdout.write(
                f"  duplicate URL: programme {collision['programme_id']} "
                f"collides with video {collision['kept_video_id']}"
            )
