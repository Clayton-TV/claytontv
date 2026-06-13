"""Harvest video runtimes from YouTube/Vimeo. Idempotent (fills nulls);
gentle on the platforms, never the legacy server. Safe on a cron.

    harvest_durations            # fill missing durations
    harvest_durations --refresh  # re-fetch everything

Needs YOUTUBE_API_KEY for the YouTube majority; Vimeo oEmbed needs no auth."""

import os

from django.core.management.base import BaseCommand

from catalogue.durations import harvest_durations


class Command(BaseCommand):
    help = "Harvest video runtimes from the hosting platforms (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("--refresh", action="store_true", help="Re-fetch durations even where already set")

    def handle(self, *args, **options):
        if not os.environ.get("YOUTUBE_API_KEY"):
            self.stdout.write(self.style.WARNING("YOUTUBE_API_KEY not set — YouTube durations will be skipped."))
        stats = harvest_durations(refresh=options["refresh"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Durations harvested — YouTube: {stats['youtube']}, Vimeo: {stats['vimeo']}, "
                f"unresolved: {stats['unresolved']}."
            )
        )
