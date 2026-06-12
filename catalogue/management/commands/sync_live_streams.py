"""Sync live/upcoming YouTube broadcasts. Two cadences, one command:

    sync_live_streams --discover   # hourly: search for new broadcasts (≈200
                                   # quota units per channel) + refresh
    sync_live_streams              # every few minutes: cheap status refresh
                                   # (1 unit) on already-known broadcasts

Needs YOUTUBE_API_KEY in the environment (key restricted to the YouTube
Data API; see docs/DEPLOYMENT.md)."""

import os

import requests
from django.core.management.base import BaseCommand

from catalogue.youtube_live import discover_broadcasts, discover_channels, refresh_statuses


class Command(BaseCommand):
    help = "Sync live/upcoming YouTube broadcasts (--discover hourly; bare = cheap refresh)"

    def add_arguments(self, parser):
        parser.add_argument("--discover", action="store_true", help="Search channels for new broadcasts (expensive)")

    def handle(self, *args, **options):
        if not os.environ.get("YOUTUBE_API_KEY"):
            # Exit cleanly so the cron can be armed before the key exists
            self.stdout.write(self.style.WARNING("YOUTUBE_API_KEY not set — skipping live-stream sync."))
            return
        session = requests.Session()
        if options["discover"]:
            channels = discover_channels(session)
            found = discover_broadcasts(session, channels)
            self.stdout.write(self.style.SUCCESS(f"Searched {len(channels)} channels; {found} broadcasts upserted."))
        else:
            checked = refresh_statuses(session)
            self.stdout.write(self.style.SUCCESS(f"Refreshed {checked} active broadcasts."))
