from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Video(models.Model):
    """Model representing a video"""
    title = models.CharField(max_length=200)
    channel = models.ForeignKey('Channel',on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the video")
    topic = models.ManyToManyField(Topic, help_text="Select topics for this video")
    series = models.ForeignKey('Series', on_delete=models.RESTRICT, null=True, blank=True)
    speaker = models.ForeignKey('Speaker',on_delete=models.RESTRICT, null=True, blank=True)
    series_number = models.IntegerField(help_text="If part of a series provide the number in the series", null=True, blank=True)
    date_created = models.DateField()
    livestream_date = models.DateField(null=True, blank=True)
    embedding_url = models.URLField(unique=True)
    bible_book = models.CharField(max_length=100, null=True, blank=True)
    ministry = models.ManyToManyField('Ministry', null=True, blank=True)
    
    class Meta:
        ordering = ['date_created']
    
    def __str__(self):
        """String for representing model object"""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the video"""
        return reverse('video-detail', args=[str(self.id)])
    
    def display_topic(self):
        """Create a string for the topics. This is required to display topics in Admin."""
        return ', '.join(topic.name for topic in self.topic.all()[:3])
    
    display_topic.short_description = 'Topics'
   