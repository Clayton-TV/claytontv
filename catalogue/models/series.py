from django.db import models
from .topic import Topic
from django.urls import reverse # generate urls by reversing url pattern


class Series(models.Model):
    """Model representing series"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=5000, null=True, blank=True)
    topic = models.ManyToManyField('Topic', null=True, blank=True)
    speaker = models.ManyToManyField('Speaker', null=True, blank=True)
    ministry = models.ManyToManyField('Ministry', null=True, blank=True)
    videos = models.ManyToManyField('Video', null=True, blank=True)
    bible_book = models.ManyToManyField('Bible_Book', null=True, blank=True)
    year_start = models.CharField(max_length=100)
    year_end = models.CharField(max_length=100)

    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("series-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']