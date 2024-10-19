# File: forms.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/19/2024
# Description: forms to process a new profile and adding status message

from django import forms
from .models import Profile, StatusMessage


class CreateProfileForm(forms.ModelForm):
    '''forms for adding another new profile'''

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'image_url'] #fields to include in the form

class CreateStatusMessageForm(forms.ModelForm):
    '''forms for add a status message for a profile'''
    class Meta:
        model = StatusMessage
        fields = ['message'] #fields to include in the form

class UpdateProfileForm(forms.ModelForm):
    '''forms to update an existing profile'''
    class Meta:
        model = Profile
        fields = ['city', 'email_address', 'image_url'] #fields to include in the form

class UpdateStatusMessageForm(forms.ModelForm):
    '''form to update an existing status message'''
    class Meta:
        model = StatusMessage
        fields = ['message'] #fields to include in the form, timestamp not needed as automatically filled