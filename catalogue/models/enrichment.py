from django.db import models


class VideoEnrichment(models.Model):
    """AI-proposed metadata for a video, stored *alongside* the Video (never
    overwriting human-authored fields). Populated by
    ``catalogue.enrichment.store_enrichment`` and folded invisibly into the
    Typesense doc for search recall; surfaced to editors as suggestions (E3) and,
    behind a flag, optionally to the public (E4).

    One row per video (OneToOne). Re-running enrichment upserts in place, so the
    row is always the latest model output for ``prompt_version``.
    """

    video = models.OneToOneField(
        "Video",
        on_delete=models.CASCADE,
        related_name="enrichment",
        help_text="The video this enrichment describes.",
    )

    summary = models.TextField(blank=True, default="", help_text="A one- or two-sentence AI summary.")
    topics = models.JSONField(default=list, blank=True, help_text="AI-suggested topic strings.")
    audience = models.CharField(max_length=200, blank=True, default="", help_text="AI-suggested audience.")
    bible_passages = models.JSONField(
        default=list,
        blank=True,
        help_text="Cross-checked Bible references: [{'book', 'label', 'chapter'?, ...}].",
    )
    keywords = models.JSONField(default=list, blank=True, help_text="AI-suggested search keywords.")

    # Provenance — which model + prompt produced this, and when. prompt_version
    # lets a prompt change invalidate + re-run cleanly (see enrichment.PROMPT_VERSION).
    model = models.CharField(max_length=100, blank=True, default="", help_text="The Ollama model that generated this.")
    prompt_version = models.PositiveIntegerField(default=0, help_text="enrichment.PROMPT_VERSION at generation time.")
    generated_at = models.DateTimeField(null=True, blank=True, help_text="When this enrichment was generated.")

    def __str__(self):
        return f"Enrichment for {self.video_id}"
