from typing import ClassVar  # Add typing imports

from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern
from urllib.parse import quote  # Import for URL encoding

# from .ministry import Ministry
# from .video import Video
# from .series import Series

CHANNEL_TYPE = (
    ("You", "Youtube"),
    ("Vim", "Vimeo"),
    ("Twt", "Twitch"),
)


class Channel(models.Model):
    """Model representing a channel that uploads videos"""

    name = models.CharField(max_length=200, help_text="The channel name.")
    summary = models.TextField(max_length=5000, null=True, blank=True, help_text="The summary of the channel")
    type = models.CharField(max_length=200, help_text="The channel type.")
    channel_url = models.URLField(unique=True, help_text="The channel url.")
    trusted = models.BooleanField(help_text="Whether the channel is trusted.")
    ministry = models.ManyToManyField(
        "Ministry",
        blank=True,
        related_name="+",
        help_text="The ministries related to the channel.",
    )
    videos = models.ManyToManyField(
        "Video",
        blank=True,
        related_name="+",
        help_text="The videos related to the channel.",
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="+",
        help_text="The series related to the channel.",
    )

    def __str__(self):
        """String for representing channel object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the channel"""
        encoded_name = quote(
            self.name, safe=""
        )  # Encode the name, escaping all special characters
        return reverse("browse_channel", args=[encoded_name])

    class Meta:
        ordering: ClassVar[list[str]] = ["name"]
