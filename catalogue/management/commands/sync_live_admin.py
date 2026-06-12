"""Incremental sync from the live legacy admin. Intended to run on a cron
while the old site survives; safe to run any time (same idempotent upserts
as the dump ingest)."""

from django.core.management.base import BaseCommand, CommandError

from catalogue.ingest.live_admin import AdminAuthError, sync


class Command(BaseCommand):
    help = "Pull the newest-modified programmes from the legacy admin and upsert them"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=2, help="List pages to scan (50 programmes each)")

    def handle(self, *args, **options):
        try:
            stats, records = sync(pages=options["pages"])
        except AdminAuthError as e:
            raise CommandError(str(e)) from e

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {len(records)} programmes from the live admin: "
                f"{stats['created']} created, {stats['updated']} updated, "
                f"{stats['skipped_no_media']} without media, "
                f"{stats['skipped_url_collision']} duplicate-URL skips."
            )
        )
