from django.db import models


class RelatedResource(models.Model):
    """An external companion to a video (transcript page, audio page, study
    material) — rescued from the legacy transcript_link/audio_link fields.
    These are links to third-party sites (printandaudio.org.uk etc.), not
    hosted files."""

    KINDS = (
        ("transcript", "Transcript"),
        ("audio", "Audio"),
        ("other", "Other"),
    )

    video = models.ForeignKey("Video", on_delete=models.CASCADE, related_name="related_resources")
    kind = models.CharField(max_length=20, choices=KINDS)
    url = models.URLField(max_length=500, help_text="Resolved destination (bit.ly already unshortened).")

    class Meta:
        constraints = (models.UniqueConstraint(fields=("video", "kind", "url"), name="unique_resource_per_video"),)

    def __str__(self):
        return f"{self.kind} for {self.video_id}"
