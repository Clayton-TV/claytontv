from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

from .series import Series
from .topic import Topic
from .video import Video

class Demographic(models.Model):
    """Model representing the demographic table, intended to allow easy segregation of the website for different user types."""
    name = models.CharField(max_length=200) # e.g. kids, searchers
    summary = models.TextField(max_length=5000)
    series = models.ManyToManyField('Series',null=True, blank=True)
    topics = models.ManyToManyField('Topic',null=True, blank=True)
    videos = models.ManyToManyField('Video',null=True, blank=True)
    thumbnail = models.CharField(max_length=200)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])