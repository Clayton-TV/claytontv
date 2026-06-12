"""Idempotent backfill of Video.is_livestream from the legacy CSV.

The original import_videos never read the IsLivestream column, so every
imported video has is_livestream=False and the Livestreams page is empty.
This updates existing videos in place (matched on ID) — no delete, no
re-link — so it can run safely against a populated database.
"""

import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import Video


class Command(BaseCommand):
    help = "Set Video.is_livestream from the IsLivestream column of CSV/Videos.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default=str(Path(settings.BASE_DIR) / "CSV" / "Videos.csv"),
            help="Path to Videos.csv",
        )

    def handle(self, *args, **options):
        live_ids = set()
        with Path(options["csv"]).open(encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                if row.get("IsLivestream", "").strip() == "1":
                    live_ids.add(row["ID"])

        promoted = Video.objects.filter(id__in=live_ids, is_livestream=False).update(is_livestream=True)
        demoted = Video.objects.filter(is_livestream=True).exclude(id__in=live_ids).update(is_livestream=False)
        total = Video.objects.filter(is_livestream=True).count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Livestream flags reconciled: +{promoted} promoted, -{demoted} demoted, {total} now flagged."
            )
        )
