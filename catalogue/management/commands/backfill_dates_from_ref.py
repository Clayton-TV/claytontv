"""One-off repair: set date_recorded from the programmeRef (id_number) for
videos the live admin left undated. Local only — no network, idempotent.

The 2026-06 backfill found 45 such programmes: the admin's date field was
blank but the ref still encodes DD.MM.YY. Without this they sink to the
bottom of every recency list (correctly, given nulls-last) despite having
a perfectly good date hiding in their reference."""

from django.core.management.base import BaseCommand

from catalogue.ingest.normalize import date_from_ref
from catalogue.models import Video


def recover_dates():
    """Fill date_recorded from id_number where possible. Returns the count
    updated; never overwrites an existing date."""
    updated = 0
    for video in Video.objects.filter(date_recorded__isnull=True).exclude(id_number=""):
        recovered = date_from_ref(video.id_number)
        if recovered:
            video.date_recorded = recovered
            video.save(update_fields=["date_recorded"])
            updated += 1
    return updated


class Command(BaseCommand):
    help = "Recover date_recorded from programmeRef for undated videos (local, idempotent)"

    def handle(self, *args, **options):
        updated = recover_dates()
        self.stdout.write(self.style.SUCCESS(f"Recovered dates for {updated} previously-undated videos."))
