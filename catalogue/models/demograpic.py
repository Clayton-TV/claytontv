from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

#from .series import Series
#from .topic import Topic
#from .video import Video

class Demographic(models.Model):
    """Model representing the demographic table, intended to allow easy segregation of the website for different user types."""
    name = models.CharField(max_length=200, help_text="The name of the demographic e.g. Kids, searchers.") # e.g. kids, searchers
    summary = models.TextField(max_length=5000, help_text='A summary/description of the demographic.')
    series = models.ManyToManyField('Series', blank=True, related_name='+', help_text="The series related to the channel.")
    topics = models.ManyToManyField('Topic', blank=True, related_name='+' , help_text="The topics related to the channel.")
    videos = models.ManyToManyField('Video', blank=True, related_name='+', help_text="The vieos related to the channel.")
    thumbnail = models.CharField(max_length=200, help_text="The thumbnail for the demographic.")

    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])