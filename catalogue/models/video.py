from typing import ClassVar, List  # Add typing imports

from django.db import models  # import the model class that all models are based on
from django.urls import reverse  # generate urls by reversing url pattern

# from .series import Series
# from .speaker import Speaker
from .bible_book import BibleBook

# from .ministry import Ministry
# from .demograpic import Demographic
from .label import Label

# Now import the models that we need to link to:
# from .channel import Channel


# Now the actual class definition for the model (database table):
class Video(models.Model):
    """Model representing the database table for videos,
    where each table entry is an individual video"""

    id_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="A unique video identifier generated e.g.YT1234",
    )

    bible_book = models.ManyToManyField(BibleBook, blank=True, help_text="The bible books covered in the video.")
    demographic = models.ManyToManyField("Demographic", blank=True, help_text="The video's demographic.")
    description = models.TextField(max_length=5000, help_text="Enter a brief description of the video <5000 chars.")
    url = models.URLField(unique=True, help_text="A link to where the video is hosted.")
    ministry = models.ManyToManyField("Ministry", blank=True, help_text="The ministries associated with the video.")
    number_in_series = models.IntegerField(
        help_text="If part of a series provide the number in the series.",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=200, help_text="The title of the video."
    )  # check max title length on popular upload sites ->>> Youtube 100 characters, Vimeo 128.
    speaker = models.ManyToManyField("Speaker", blank=True, help_text="The speakers/artist in the video.")
    is_livestream = models.BooleanField(default=False, help_text="Whether the video was a live stream.")
    topic = models.ManyToManyField("Topic", help_text="Select topics for this video.")

    date_recorded = models.DateField(null=True, blank=True, help_text="The date the video was recorded.")
    date_created = models.DateField(help_text="The date a video is uploaded.")
    date_modified = models.DateField(null=True, blank=True, help_text=" The last time the video data was edited.")

    labels = models.ForeignKey(
        Label,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        help_text="Labels for internal admin use.",
    )
    channel = models.ForeignKey(
        "Channel",
        on_delete=models.RESTRICT,
        null=True,
        help_text="The channel for the video.",
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        help_text="The series the video is part of.",
    )

    class Meta:
        ordering: ClassVar[list[str]] = ["date_created"]

    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the video"""
        return reverse("video-detail", args=[str(self.id)])

    def display_topic(self):
        """Create a string for the topics. This is required to display topics in Admin."""
        return ", ".join(topic.name for topic in self.topic.all()[:3])

    display_topic.short_description = "Topics"
