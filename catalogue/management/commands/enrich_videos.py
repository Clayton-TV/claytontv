"""Print AI metadata suggestions for catalogue videos (PoC — issue #201).

Calls the self-hosted Ollama model (``catalogue/enrichment.py``) for one or
more videos and prints a readable suggestions report. **Dry-run by default —
nothing is written to the database.** This is a proof of concept; persisting
suggestions belongs behind a human-review UI (next step).

Examples::

    uv run poe manage enrich_videos                # first 5 videos, dry-run
    uv run poe manage enrich_videos --limit 10
    uv run poe manage enrich_videos --id 1234
    uv run poe manage enrich_videos --model gemma4:26b-a4b-it-qat
"""

from django.core.management.base import BaseCommand, CommandError

from catalogue.enrichment import enrich_video
from catalogue.models.video import Video


class Command(BaseCommand):
    help = "Print AI metadata suggestions for videos via Ollama (PoC, does not write to the DB)."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="How many videos to enrich (default: 5).")
        parser.add_argument("--id", dest="video_id", help="Enrich a single video by its primary key.")
        parser.add_argument("--model", help="Override the Ollama model (default: settings.OLLAMA['model']).")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help="Print only, never write (default and only supported mode in this PoC).",
        )

    def handle(self, *args, **options):
        videos = self._select_videos(options)
        if not videos:
            self.stdout.write(self.style.WARNING("No videos matched."))
            return

        self.stdout.write(self.style.NOTICE(f"Enriching {len(videos)} video(s) — DRY RUN, nothing will be written.\n"))
        for video in videos:
            self._report(video, options.get("model"))

    def _select_videos(self, options):
        video_id = options.get("video_id")
        if video_id:
            try:
                return [Video.objects.get(pk=video_id)]
            except Video.DoesNotExist as exc:
                raise CommandError(f"No video with id {video_id!r}.") from exc
        return list(Video.objects.all()[: options["limit"]])

    def _report(self, video, model):
        self.stdout.write(self.style.HTTP_INFO("=" * 72))
        self.stdout.write(self.style.HTTP_INFO(f"Video {video.pk}: {video.name}"))
        self.stdout.write("=" * 72)

        suggestions = enrich_video(video, model=model)

        self._line("Summary", suggestions["summary"] or "(none)")
        self._line("Audience", suggestions["suggested_audience"] or "(none)")
        self._line("Topics", ", ".join(suggestions["suggested_topics"]) or "(none)")
        self._line("Keywords", ", ".join(suggestions["keywords"]) or "(none)")

        passages = suggestions["bible_passages"]
        if passages:
            self._line("Bible passages", ", ".join(p["label"] for p in passages))
        else:
            self._line("Bible passages", "(none)")
        self.stdout.write("")

    def _line(self, label, value):
        self.stdout.write(f"  {label:<15} {value}")
