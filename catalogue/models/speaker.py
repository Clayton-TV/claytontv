from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern

# from .video import Video
# from .series import Series


class Speaker(models.Model):
    """Model representing speakers"""

    name = models.CharField(max_length=200, help_text="The name of the speaker.")
    bio = models.TextField(max_length=5000, help_text="The biography of the speaker.")
    videos = models.ManyToManyField(
        "Video", blank=True, related_name="+", help_text="The videos related to video."
    )
    series = models.ManyToManyField(
        "Series",
        blank=True,
        related_name="+",
        help_text="The videos related to series.",
    )
    thumbnail = models.CharField(
        max_length=200, help_text="The thumbnail for the speaker."
    )

    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])

    class Meta:
        ordering = ["name"]
