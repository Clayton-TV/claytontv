from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Channel(models.Model):
    """Model representing a channel that uploads videos"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=1000, null=True, blank=True)
    
    def __str__(self):
        """String for representing channel object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the channel"""
        return reverse("channel-detail", args=[str(self.id)])