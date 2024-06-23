from django.db import models
from django.urls import reverse # generate urls by reversing url pattern
from .video import Video
from .series import Series


class Speaker(models.Model):
    """Model representing speakers"""
    name = models.CharField(max_length=200)
    bio = models.TextField(max_length=5000)
    videos = models.ManyToManyField('Video',null=True,blank=True)
    series = models.ManyToManyField('Series',null=True, blank=True)
    thumbnail = models.CharField(max_length=200)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])

    class Meta:
        ordering = ['name']