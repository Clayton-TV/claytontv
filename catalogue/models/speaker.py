from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Speaker(models.Model):
    """Model representing speakers"""
    name = models.CharField(max_length=200)
    bio = models.TextField(max_length=1000)
    series = models.ManyToManyField('Series',null=True, blank=True)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])