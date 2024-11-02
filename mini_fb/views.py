# File: views.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/1/2024
# Description: presentation to the user: showall profiles and detail profiles
#creating profile and status message, and redirecting/rendering

from django.shortcuts import render
from .models import Profile, StatusMessage, Image
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView

from .forms import *

from typing import Any
from django.urls import reverse

from django.http import HttpResponseRedirect

import random


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect


class ShowAllProfilesView(ListView):
    '''Create a subclass of ListView to display all profile.'''
    model = Profile # retrieve objects of type Profile from the database
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'  ##read the object from databse(entirely!, all attributes)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = None

        if self.request.user.is_authenticated:
            # Attempt to retrieve the profile associated with the logged-in user
            user_profile = Profile.objects.filter(user=self.request.user).first()
        
        context['user_profile'] = user_profile
        return context    
    

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

    def get_context_data(self, **kwargs):
        #get context data for creating new user
        context = super().get_context_data(**kwargs)
        # Add UserCreationForm to the context
        if not self.request.user.is_authenticated:
            context['user_creation_form'] = UserCreationForm()
        return context
   
    
    def dispatch(self, request, *args, **kwargs):
        #handle logic when trying to create new profile
        if request.user.is_authenticated:
            # If user has a profile, redirect them to the main page
            if Profile.objects.filter(user=request.user).exists():
                return HttpResponseRedirect(reverse('mini_fb:show_all'))
   
        return super().dispatch(request, *args, **kwargs)
    
    
    
    def form_valid(self, form):
        #  Reconstruct UserCreationForm from POST data
        if self.request.POST:
            user_creation_form = UserCreationForm(self.request.POST)
        
        # Check if UserCreationForm is valid before proceeding
        if user_creation_form.is_valid():
           #Save the new user and get the created User instance
            new_user = user_creation_form.save()
            
            #Attach the new user to the profile instance and log then in
            form.instance.user = new_user
            login(self.request, new_user)
            
            # Delegate the rest to the super class’ form_valid method
            return super().form_valid(form)
        else:
          #invalid form
            return self.form_invalid(form)



class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    '''A view to create comments on article
        on get: send back the for for dispay
        on post: rewad/process the form and save it to the DB
    '''

    form_class = CreateStatusMessageForm #form that forms.py has
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs:Any) -> dict[str, Any]:

        #get the context data, which profile are we accessing?
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['profile'] = profile
        return context
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def get_object(self):
        #get profile related to self
        return Profile.objects.get(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        #logichandling when trying to create new message: must be correct user
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        # Get the message to be deleted
        profile = self.get_object()
        # Only allow deletion if the user owns the message
        if profile.user != request.user:
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)    

    

    def get_success_url(self) -> str:
        '''once created message, redirect back to the profile page, showing the message along with profile info'''
        #updated as we changed structure, pk needs to be obtained in anotehr way
        return reverse('mini_fb:show_profile', kwargs={'pk': self.get_object().pk})


    def form_valid(self, form):
        ###self.kwargs shows the pk, form.cleane_data shows the fields with its argument

        profile = self.get_object()

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
        

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''updating profile view'''
    form_class = UpdateProfileForm #form that forms.py has
    template_name = "mini_fb/update_profile_form.html" #html page which tells where to go
    model = Profile

    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def get_object(self, queryset=None):
        #get profile of self
        return Profile.objects.get(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        # Get the message to be deleted
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        profile = self.get_object()
        # Only allow deletion if the user owns the message
        
        if profile.user != request.user:
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)


class  DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
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
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def dispatch(self, request, *args, **kwargs):
        #see if user is logged in or not, make sure it's the same user
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        # Get the message to be deleted
        message = self.get_object()
        # Only allow deletion if the user owns the message
        if message.profile.user != request.user:
            profile = message.profile
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)

class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
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
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def dispatch(self, request, *args, **kwargs):
        #make sure it's the right owner of message
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        # Get the message to be deleted
        message = self.get_object()
        # Only allow deletion if the user owns the message
        if message.profile.user != request.user:
            profile = message.profile
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)


class CreateFriendView(LoginRequiredMixin, View):
    '''newly defined create friend view, no model/template needed '''
   
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def get_object(self):
        #get the profile of self
        return Profile.objects.get(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        #make sure user is logged in
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')

        profile = self.get_object()
        other_profile = Profile.objects.get(pk=other_pk)
        if profile.user != request.user:
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)

        # Only add as friend if the profiles are not the same
        if pk != other_pk:
            profile.add_friend(other_profile)

        # Redirect to the profile page after adding the friend
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
        profile = self.get_object()
        friend_suggestions = profile.get_friend_suggestions()
        
        context['friend_suggestions'] = friend_suggestions

        return context
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def get_object(self, queryset=None):
        #get self object
        return Profile.objects.get(user=self.request.user)

    
    def dispatch(self, request, *args, **kwargs):
        #make sure it's logged in
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        # Get the message to be deleted
        profile = self.get_object()
        # Only allow deletion if the user owns the message
        if profile.user != request.user:
            #do not allow if the user aren't the sae
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)


class ShowNewsFeedView(DetailView):
    '''showing news feed for this person and all its friend'''
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        '''get news feed by using method implemented in Profile class from models.py'''
        context = super().get_context_data(**kwargs)

        # Get the news feed for the current profile

        news_feed = self.get_object().get_news_feed()
        context['news_feed'] = news_feed

        return context
    
    def get_login_url(self) -> str:
        return reverse('mini_fb:login')
    
    def get_object(self, queryset=None):
        #get profile of self
        return Profile.objects.get(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        #make sure it's logged in
        if not request.user.is_authenticated:
            return redirect('mini_fb:login')
        # Get the message to be deleted
        profile = self.get_object()
        # Only allow deletion if the user owns the message
        if profile.user != request.user:
            profile_url = reverse('mini_fb:show_profile', args=[profile.pk])
            return HttpResponseRedirect(profile_url)
        return super().dispatch(request, *args, **kwargs)
    

