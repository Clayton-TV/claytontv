"""Clean existing Topic names and merge the duplicates that cleaning reveals.

The ingest cleaners (`clean_topic_name`) already normalise *new* data, but rows
imported before them keep depth-prefix / mojibake names (e.g. a triple
minus-sign prefix on "The Grace of God"). Re-cleaning some names makes them identical
to an already-clean topic — those are merged **deterministically** (no judgment):
videos are re-pointed via the `Video.topic` M2M to the topic with the most
videos, then the now-empty duplicate is deleted.

Idempotent — a second run is a no-op. Safe to re-run after deploys until the
Epic 2 importer rework owns this. Genuine typo dups that differ by *case*
("Christian Life" vs "Christian LIfe") are NOT touched here — those need human
judgment (the Slice 6 taxonomy-merge tool, docs/STUDIO_TAXONOMY.md).
"""

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from catalogue.ingest.normalize import clean_topic_name
from catalogue.models.topic import Topic


class Command(BaseCommand):
    help = "Clean topic names (depth/mojibake prefixes) and merge the duplicates that reveals. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing.")

    def handle(self, *args, dry_run=False, **options):
        groups = defaultdict(list)
        for topic in Topic.objects.annotate(video_total=Count("video")):
            key = clean_topic_name(topic.name)
            if key:  # never collapse a name to empty
                groups[key].append(topic)

        renamed = merged = 0
        for clean, topics in groups.items():
            topics.sort(key=lambda t: t.video_total, reverse=True)
            canonical, *losers = topics

            if canonical.name != clean:
                self.stdout.write(f"rename: {canonical.name!r} -> {clean!r}")
                renamed += 1
                if not dry_run:
                    canonical.name = clean
                    canonical.save()

            for loser in losers:
                self.stdout.write(f"merge:  {loser.name!r} ({loser.video_total} videos) -> {clean!r}")
                merged += 1
                if not dry_run:
                    with transaction.atomic():
                        videos = list(loser.video_set.all())
                        for video in videos:
                            video.topic.add(canonical)
                        loser.delete()
                        # M2M writes don't fire post_save — re-save each moved video
                        # so its search doc reflects the canonical topic.
                        for video in videos:
                            video.save()

        verb = "would " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(f"Done: {verb}rename {renamed}, {verb}merge {merged}."))
