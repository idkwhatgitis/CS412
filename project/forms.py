# File: forms.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/19/2024
# Description: forms to process a new profile and adding status message

from django import forms
from .models import *

class CreateCustomerForm(forms.ModelForm):
    class Meta: 
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'address',
            "email_address",
            "phone_number",
            "image_self"
            ]
        labels = {
            'image_self': 'Image',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email_address': 'Email Address',
            'phone_number': 'Phone Number',
        }

class UpdateCustomerForm(forms.ModelForm):
    class Meta: 
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'address',
            "email_address",
            "phone_number",
            "image_self"
            ]
        labels = {
            'image_self': 'Image',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email_address': 'Email Address',
            'phone_number': 'Phone Number',
        }

class CreateItemForm(forms.ModelForm):
    class Meta: 
        model = Item
        fields = [
            'title',
            'description',
            'price',
            'quantity_left'
            ]
        

class UpdateItemForm(forms.ModelForm):
    class Meta: 
        model = Item
        fields = [
            'title',
            'description',
            'price',
            'quantity_left'
            ]
        

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'image_self']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }
        labels = {
            'image_self': 'Add image'
        }
