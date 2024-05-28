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
