from django.db import models
from django.urls import reverse # generate urls by reversing url pattern
  
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
        return reverse("series-detail", args=[str(self.id)])
    
    class Meta:
        ordering = ['name']
    
