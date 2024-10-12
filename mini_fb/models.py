# File: models.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/11/2024
# Description: models used for mini_fb: profile and status message

from django.db import models
from django.urls import reverse

# Create your models here.


class Profile(models.Model):
    #attributes:

    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    image_url = models.URLField(blank=True) ##image field 

    def get_absolute_url(self) -> str:
        '''upon successfully creating a profile, redirect to the newly created profile page'''
        return reverse('mini_fb:show_profile', args=[str(self.pk)])

    def __str__(self):
        '''string representation of the object'''

        return f"{self.first_name} by {self.last_name} by {self.city} by {self.email_address}"
    
    def get_status_messages(self):
        '''get all the messages of this profile'''
        status_message = StatusMessage.objects.filter(profile=self)
        return status_message


class StatusMessage(models.Model):
    '''class for status message and its attribute'''
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey("Profile", on_delete = models.CASCADE)
    
    def __str__(self):
        '''string representation of this object'''
        return f'{self.message}'

