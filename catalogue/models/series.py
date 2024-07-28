from django.db import models
from django.urls import reverse # generate urls by reversing url pattern
#from .topic import Topic
#from .speaker import Speaker
#from .ministry import Ministry
#from .video import Video
from .bible_book import Bible_Book



class Series(models.Model):
    """Model representing series"""
    name = models.CharField(max_length=200, help_text="The name of the series.")
    summary = models.TextField(max_length=5000, null=True, blank=True, help_text= 'The summary/description of the series.')
    topic = models.ManyToManyField('Topic', null=True, blank=True, related_name='+', help_text= 'The topic related to the series.')
    speaker = models.ManyToManyField('Speaker', null=True, blank=True, related_name='+', help_text= 'The speaker related to the series.')
    ministry = models.ManyToManyField('Ministry', null=True, blank=True, related_name='+', help_text= 'The ministry related to the series.')
    videos = models.ManyToManyField('Video', null=True, blank=True, related_name='+', help_text= 'The videos related to the series.')
    bible_book = models.ManyToManyField(Bible_Book, null=True, blank=True, help_text= 'The Bible books related to the series.')
    year_start = models.CharField(max_length=100, help_text= 'The year the series started.')
    year_end = models.CharField(max_length=100, help_text= 'The year the series ended.')

    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("series-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']