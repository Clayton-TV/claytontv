from django.db import models    # import the model class that all models are based on
from django.urls import reverse # generate urls by reversing url pattern

# Now import the models that we need to link to:
from .channel import Channel    
from .topic import Topic
from .series import Series
from .speaker import Speaker
from .bible_book import Bible_Book
from .ministry import Ministry
from .demograpic import Demographic
from .label import Label


# Now the actual class definition for the model (database table):
class Video(models.Model): 
    """Model representing the database table for videos,
    where each table entry is an individual video"""
    demographic = models.ManyToManyField('Demographic', null=True, blank=True)
    url = models.URLField(unique=True)
    id_number = models.CharField(max_length=100,unique=True)
    labels = models.ForeignKey('Label',null=True, blank=True)
    ministry = models.ManyToManyField('Ministry', null=True, blank=True)
    series = models.ForeignKey('Series', on_delete=models.RESTRICT, null=True, blank=True)
    number_in_series = models.IntegerField(help_text="If part of a series provide the number in the series", null=True, blank=True)
    name = models.CharField(max_length=200) # check max title length on popular upload sites
    description = models.TextField(max_length=5000, help_text="Enter a brief description of the video")
    speaker = models.ManyToManyField('Speaker',on_delete=models.RESTRICT, null=True, blank=True)
    bible_book = models.ManyToManyField('Bible_book', on_delete=models.RESTRICT, null=True, blank=True)
    date_recorded = models.DateField(null=True, blank=True)
    date_created = models.DateField()
    date_modified = models.DateField(null=True, blank=True)
    is_livestream = models.BooleanField(default=False)
    channel = models.ForeignKey('Channel',on_delete=models.RESTRICT, null=True)
    topic = models.ManyToManyField(Topic, help_text="Select topics for this video")

    
    class Meta:
        ordering = ['date_created']
    
    def __str__(self):
        """String for representing model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the video"""
        return reverse('video-detail', args=[str(self.id)])
    
    def display_topic(self):
        """Create a string for the topics. This is required to display topics in Admin."""
        return ', '.join(topic.name for topic in self.topic.all()[:3])
    
    display_topic.short_description = 'Topics'
   