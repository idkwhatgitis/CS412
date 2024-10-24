# File: views.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/19/2024
# Description: presentation to the user: showall profiles and detail profiles
#creating profile and status message, and redirecting/rendering

from django.shortcuts import render
from .models import Profile, StatusMessage, Image
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from .forms import *

from typing import Any
from django.urls import reverse

from django.http import HttpResponseRedirect

import random

class ShowAllProfilesView(ListView):
    '''Create a subclass of ListView to display all profile.'''
    model = Profile # retrieve objects of type Profile from the database
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'  ##read the object from databse(entirely!, all attributes)
    

class ShowProfilePageView(DetailView):
    '''show a specific profile from the databse'''
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    '''A view to create message on profile
        on get: send back the for for dispay
        on post: read/process the form and save it to the DB
    '''

    form_class = CreateProfileForm #form that forms.py has
    template_name = "mini_fb/create_profile_form.html"


class CreateStatusMessageView(CreateView):
    '''A view to create comments on article
        on get: send back the for for dispay
        on post: rewad/process the form and save it to the DB
    '''

    form_class = CreateStatusMessageForm #form that forms.py has
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs:Any) -> dict[str, Any]:

        #get the context data, which profile are we accessing?
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        context['profile'] = profile
        return context



    def get_success_url(self) -> str:
        '''once created message, redirect back to the profile page, showing the message along with profile info'''
        return reverse('mini_fb:show_profile', kwargs=self.kwargs)


    def form_valid(self, form):
        ###self.kwargs shows the pk, form.cleane_data shows the fields with its argument

        profile = Profile.objects.get(pk=self.kwargs['pk'])

        #attach the article to the instance of cmoment
        form.instance.profile = profile

        sm = form.save()

        # Read the files from the multi-part form data
        files = self.request.FILES.getlist('files')

        for file in files:
        # Create a new Image object
            image = Image(statusMessage=sm, image_url=file)
        # Save the Image object to the database
            image.save()
        return super().form_valid(form)
        

class UpdateProfileView(UpdateView):
    '''updating profile view'''
    form_class = UpdateProfileForm #form that forms.py has
    template_name = "mini_fb/update_profile_form.html" #html page which tells where to go
    model = Profile

class  DeleteStatusMessageView(DeleteView):
    '''deleting status message view, used for deletion'''
    template_name = "mini_fb/delete_status_form.html" #html page which tells where to go
    model = StatusMessage
    context_object_name = 'status_message' #self define a message name

    def get_success_url(self):
        '''Return a the URL to which we should be directed after the deletion(previous page)'''
        # get the pk for this comment
        pk = self.kwargs.get('pk')
        message = StatusMessage.objects.filter(pk=pk).first() # get one object from QuerySet
        
        # find the article to which this message is related by FK
        profile = message.profile
        # reverse to show the page
        return reverse('mini_fb:show_profile', kwargs={'pk':profile.pk})

class UpdateStatusMessageView(UpdateView):
    '''updating status message '''
    form_class= UpdateStatusMessageForm #form that accomplish this action
    template_name="mini_fb/update_status_message_form.html"  #html page which tells where to go
    model = StatusMessage
    context_object_name='status_message' #self define the name to use in html file

    def get_success_url(self):
        '''Return a the URL to which we should be directed after the update'''
        status_message = self.get_object()  # Get the current StatusMessage
        #return to the previous page
        return reverse('mini_fb:show_profile', kwargs={'pk': status_message.profile.pk})


class CreateFriendView(View):
    '''newly defined create friend view, no model/template needed '''
    def dispatch(self, request, *args, **kwargs):

        '''overwrite dispatch maehod'''
        # Get the profile pk and other_pk from the URL
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        if (pk!=other_pk):
            profile = Profile.objects.get(pk=pk)
            other_profile = Profile.objects.get(pk=other_pk)
            profile.add_friend(other_profile)
        # Add the other profile as a friend

        profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
        return HttpResponseRedirect(profile_url)
    
class ShowFriendSuggestionsView(DetailView):
    '''showing friend suggestion for any given profile'''
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        '''get the friend suggestions from implemented method in model.py Profile class'''

        context = super().get_context_data(**kwargs)
        
        # Get friend suggestions for the current profile
        #profile = self.object
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        friend_suggestions = profile.get_friend_suggestions()
        
        context['friend_suggestions'] = friend_suggestions

        return context

class ShowNewsFeedView(DetailView):
    '''showing news feed for this person and all its friend'''
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        '''get news feed by using method implemented in Profile class from models.py'''
        context = super().get_context_data(**kwargs)

        # Get the news feed for the current profile
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        news_feed = profile.get_news_feed()

        context['news_feed'] = news_feed

        return context