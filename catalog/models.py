from django.db import models
from django.urls import reverse # generate urls by reversing url pattern

class Topic(models.Model):
    """Model representing video topics"""
    name = models.CharField(
            max_length=200,
            unique=True,
            help_text="Enter a topic or theme")
    #sub_topic needed, maybe a class inheriting from Topic? Eg. am/pm for services and bible books for 'bible teaching' topic?
    # or possibly add these as a nested json? Need tothink about this.
    summary = models.TextField(max_length=1000,null=True,blank=True)
    
    
    def __str__(self):
        """String for representing the model object"""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular topic instance"""
        return reverse('topic-detail', args=[str(self.id)])


class Video(models.Model):
    """
    Model representing a video
    NB: making all of these except the id to allow null (i.e. blank) to make importing old data from the spreadsheet
    more viable. This may want to be restricted later?
    """
    IDnum = models.CharField(unique=True,max_length=20,null=True)
    title = models.CharField(max_length=200)
    channel = models.ForeignKey('Channel',on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the video",null=True, blank=True)
    topic = models.ManyToManyField(Topic, help_text="Select topics for this video")
    series = models.ForeignKey('Series', on_delete=models.RESTRICT, null=True, blank=True)
    speaker = models.ForeignKey('Speaker',on_delete=models.RESTRICT, null=True, blank=True)
    series_number = models.IntegerField(help_text="If part of a series provide the number in the series", null=True, blank=True)
    date_created = models.DateField(null=True,blank=True)
    livestream_date = models.DateField(null=True, blank=True)
    embedding_url = models.URLField(unique=True)
    bible_book = models.ManyToManyField('BibleBook')
    ministry = models.ManyToManyField('Ministry')
    label_series = models.CharField(max_length=100, null=True,blank=True) # these label_blah attributes are for the internal master copy labels
    label_subseries = models.CharField(max_length=100, null=True,blank=True)
    label_episode = models.CharField(max_length=100, null=True,blank=True)
    IsLivestream = models.BooleanField(null=True,blank=True)
    demographic = models.ForeignKey('Demographic',on_delete=models.RESTRICT, null=True, blank=True)
    
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
    
class Speaker(models.Model):
    """Model representing speakers"""
    name = models.CharField(max_length=200)
    bio = models.TextField(max_length=1000)
    series = models.ManyToManyField('Series')
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the speaker"""
        return reverse("speaker-detail", args=[str(self.id)])
    
class Series(models.Model):
    """Model representing series"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=100, null=True, blank=True)
    topic = models.ManyToManyField(Topic)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("series-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']
    
    
class Ministry(models.Model):
    """Model representing ministy types"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=100, null=True, blank=True)
    topic = models.ManyToManyField(Topic)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("ministry-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']
    
class BibleBook(models.Model):
    """Model representing bible books, category should be 'wisdom, letters, history, prophecy, apocolyptic etc."""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50)
    series = models.ManyToManyField(Series)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("bible-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']


class Demographic(models.Model):
    """Model representing demographic types, i.e. Adult, Youth, Kids"""
    name = models.CharField(max_length=200)
    summary = models.TextField(max_length=100, null=True, blank=True)
    topic = models.ManyToManyField(Topic)
    Series = models.ManyToManyField(Series)
    Ministry = models.ManyToManyField(Ministry)
    
    def __str__(self):
        """String for representing model object"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detailed record for the series"""
        return reverse("demographic-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']