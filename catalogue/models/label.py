from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Label(models.Model):
    """Model representing a table for the admin labels to denote the video type and storage"""
    #these are admin labels so strings are correct
    label_series = models.CharField(max_length=1000, help_text="Admin Label Related to the video's series.")
    label_subseries = models.CharField(max_length=1000, help_text="Admin Label Related to the video's subseries.")
    label_episode = models.CharField(max_length=1000, help_text="Admin Label Related to the video's episode.")
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])