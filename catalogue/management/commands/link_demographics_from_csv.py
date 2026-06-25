"""Recover Video↔Demographic links from the legacy CSV export.

The dump and live-admin ingest paths never captured demographics (the admin
meta form has no demographic field — only Genre/Group, which are unrelated),
so Kids/Youth/Adults pages were empty. The legacy CSV carries the tags as a
comma-separated column; this restores them, keyed on legacy id. Local,
idempotent, no network.

Covers the CSV's content (pre-Oct-2024 bulk). Programmes added since the CSV
have no demographic source yet."""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalogue.models import Demographic, Video

# CSV uses lowercase singular tags; the model rows are title-case.
TAG_TO_NAME = {"adult": "Adults", "kids": "Kids", "youth": "Youth"}

DEFAULT_CSV = Path(__file__).resolve().parents[3] / "CSV" / "Videos.csv"


def link_demographics(csv_path):
    demographics = {name: Demographic.objects.get_or_create(name=name)[0] for name in TAG_TO_NAME.values()}
    have = set(Video.objects.values_list("id", flat=True))

    linked = 0
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            video_id = (row.get("ID") or "").strip()
            if video_id not in have:
                continue
            tags = (row.get("Demographic") or "").lower().split(",")
            names = {TAG_TO_NAME[t] for raw in tags if (t := raw.strip()) in TAG_TO_NAME}
            if not names:
                continue
            Video.objects.get(id=video_id).demographic.set(demographics[name] for name in names)
            linked += 1
    return linked


class Command(BaseCommand):
    help = "Restore Video↔Demographic links from the legacy CSV (local, idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to the legacy Videos.csv")

    def handle(self, *args, **options):
        path = options["csv"]
        if not Path(path).exists():
            raise CommandError(f"No such CSV: {path}")
        linked = link_demographics(path)
        self.stdout.write(self.style.SUCCESS(f"Linked demographics for {linked} videos."))
