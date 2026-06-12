from django.db import models


class LiveStream(models.Model):
    """A live or scheduled YouTube broadcast, synced by sync_live_streams.

    Separate from Video on purpose: these rows are ephemeral operational
    state (the homepage's "live now" / "next service" slot), not catalogue
    content. The recording becomes a Video later via the normal sync.
    """

    STATUS_CHOICES = (("upcoming", "Upcoming"), ("live", "Live"), ("ended", "Ended"))

    video_id = models.CharField(max_length=20, unique=True, help_text="YouTube video id")
    channel_id = models.CharField(max_length=40)
    channel_title = models.CharField(max_length=200, blank=True, default="")
    title = models.CharField(max_length=300)
    thumbnail = models.TextField(null=True, blank=True)
    scheduled_start = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="upcoming")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

    def __str__(self):
        return f"[{self.status}] {self.title}"
