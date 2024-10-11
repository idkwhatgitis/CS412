from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView, DetailView, CreateView

from .forms import *

from typing import Any
from django.urls import reverse

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

        return super().form_valid(form)
        
# Create your views here.
