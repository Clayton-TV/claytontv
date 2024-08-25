from django.db import models
from django.urls import reverse  # generate urls by reversing url pattern


# from .video import Video
# from .series import Series
# from .channel import Channel


class Ministry(models.Model):
    """Model representing ministry types"""
    name = models.CharField(
        max_length=200,
        help_text="The ministry's name."
    )
    summary = models.TextField(
        max_length=5000,
        null=True,
        blank=True,
        help_text="A brief summary of the ministry."
    )
    videos = models.ManyToManyField(
        'Video',
        null=True,
        blank=True,
        related_name='+',
        help_text="The videos associated with ministry."
    )
    series = models.ManyToManyField(
        'Series',
        null=True,
        blank=True,
        related_name='+',
        help_text="The series associated with minsitry."
    )
    channel = models.ManyToManyField(
        'Channel',
        null=True,
        blank=True,
        related_name='+',
        help_text="The channels associated with minsitry."
    )
    thumbnail = models.CharField(
        max_length=200,
        help_text="The thumbnail for the ministry area."
    )

    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("series-detail", args=[str(self.id)])

    class Meta:
        ordering = ['name']
