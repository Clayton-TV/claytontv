from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Topic(models.Model):
    """Model representing video topics"""
    name = models.CharField(
            max_length=200,
            unique=True,
            help_text="Enter a topic or theme")
    #sub_topic needed, maybe a class inheriting from Topic? Eg. am/pm for services and bible books for 'bible teaching' topic?
    
    
    def __str__(self):
        """String for representing the model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular topic instance"""
        return reverse('topic-detail', args=[str(self.id)])


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
    
    class Meta:
        ordering = ['date_created']
    
    def __str__(self):
        """String for representing model object"""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the video"""
        return reverse('video-detail', args=[str(self.id)])
   
class Channel(models.Model):
    """Model representing a channel that uploads videos"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=1000, null=True, blank=True)
    
    def __str__(self):
        """String for representing channel object"""
        return self.name
    
    def get_absolute_url(self):
        return reverse("channel_detail", args=[str(self.id)])
    
class Speaker(models.Model):
    """Model representing speakers"""
    name = models.CharField(max_length=200)
    bio = models.TextField(max_length=1000)
    series = models.ManyToManyField('Series')
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        return reverse("speaker_detail", args=[str(self.id)])
    
class Series(models.Model):
    """Model representing series"""
    name = models.CharField(max_length=200)
    topic = models.ManyToManyField(Topic)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        return reverse("series_detail", args=[str(self.id)])
    
    
    
    
