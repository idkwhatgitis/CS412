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
