from django.db import models

# from .video import Video
# from .series import Series
from django.urls import reverse  # generate urls by reversing url pattern
from urllib.parse import quote  # Import for URL encoding

class Topic(models.Model):
    """Model representing video topics"""

    name = models.CharField(
        max_length=200, unique=True, help_text="Enter a topic or theme"
    )
    summary = models.TextField(
        max_length=5000,
        help_text="Enter a brief summary of the topic",
        null=True,
        blank=True,
    )
    category = models.CharField(
        max_length=200, unique=True, help_text="Enter the category of the topic"
    )
    videos = models.ManyToManyField(
        "Video", help_text="Select videos for this topic", related_name="+", blank=True
    )
    series = models.ManyToManyField(
        "Series", help_text="Select series for this topic", related_name="+", blank=True
    )
    # sub_topic needed, maybe a class inheriting from Topic? Eg. am/pm for services and bible books for 'bible teaching' topic?

    def __str__(self):
        """String for representing the model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular topic instance"""
        encoded_name = quote(self.name, safe="")  # Encode the name, escaping all special characters
        return reverse("browse_topic", args=[encoded_name])

    class Meta:
        ordering = ["name"]
