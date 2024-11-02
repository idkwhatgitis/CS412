# File: models.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/1/2024
# Description: models used for mini_fb: profile and status message

from django.db import models
from django.urls import reverse

from django.db.models import Q
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
    #attributes:

    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    image_url = models.URLField(blank=True) ##image field 
    user = models.ForeignKey(User, on_delete=models.CASCADE) #newly added feature for login/logout

    def get_absolute_url(self) -> str:
        '''upon successfully creating a profile, redirect to the newly created profile page'''
        return reverse('mini_fb:show_profile', args=[str(self.pk)])

    def __str__(self):
        '''string representation of the object'''

        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        '''get all the messages of this profile'''
        status_message = StatusMessage.objects.filter(profile=self)
        return status_message


    def get_friends(self):
        '''find the friend that we already added given self'''
        profiles = Friend.objects.filter(profile1=self) | Friend.objects.filter(profile2=self)
        return profiles
    
    def add_friend(self, other):
        '''Add a friend relationship between self and another Profile instance.'''
        # Check if the friend relationship already exists
        existing_friend = Friend.objects.filter(
            (Q(profile1=self) & Q(profile2=other)) |
            (Q(profile1=other) & Q(profile2=self)) |
            (Q(profile1=self) & Q(profile2=self))
        ).exists()

        if not existing_friend:
            Friend.objects.create(profile1=self, profile2=other)
    
    def get_friend_suggestions(self):
        '''find friend suggestions for current profile satisfying constraints'''
        # Get all friend relationships involving this profile
        friends = Friend.objects.filter(Q(profile1=self) | Q(profile2=self))

        friend_ids = {self.pk}  # Start with the current profile's ID
        for friend in friends:
            if friend.profile1 == self:
                friend_ids.add(friend.profile2.pk)
            else:
                friend_ids.add(friend.profile1.pk)

        # Find profiles that are not in the friend_ids set
        suggestions = Profile.objects.exclude(pk__in=friend_ids)

        return suggestions
    
    def get_news_feed(self):
        '''find the news feed related to this person(profile)'''

        friends = self.get_friends()
        my_message = StatusMessage.objects.filter(profile=self)

        friends_profiles = [f.profile1 if f.profile2 == self else f.profile2 for f in friends]
        friends_message = StatusMessage.objects.filter(profile__in=friends_profiles)
   
        news_feed = my_message | friends_message
    
        news_feed = news_feed.order_by('-timestamp')
        return news_feed

        

class StatusMessage(models.Model):
    '''class for status message and its attribute'''
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey("Profile", on_delete = models.CASCADE)
    
    def __str__(self):
        '''string representation of this object'''
        return f'{self.message}'
    
    def get_images(self):
        '''Returns a QuerySet of all Images related to this StatusMessage'''
        return Image.objects.filter(statusMessage=self)

class Image(models.Model):
    '''class for message, which connects to another statue message'''
    '''status message can have 0 or more images'''
    '''an image can only link to 1 status message'''
    statusMessage = models.ForeignKey("StatusMessage", on_delete=models.CASCADE)
    image_url = models.ImageField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''string representation of this object'''
        return f'image of {self.statusMessage}'

class Friend(models.Model):

    profile1 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name='profile1')
    profile2 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name='profile2')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.first_name}'
    
