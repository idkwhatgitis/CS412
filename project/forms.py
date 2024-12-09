# File: forms.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/08/2024
# Description: forms to process a new customer and updating existing customer
# creating a new itm and updating an existing item
# and lastly, chat between 2 people

from django import forms
from .models import *

class CreateCustomerForm(forms.ModelForm):
    '''form to add a new customer, which appears during registration
    with fields specified in variable 'fields', and changing the name that 
    customer sees while filling out the form, with name labeled in the variable 'labels'
    '''

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
    '''form to update an existing customer, which appears once user decides to update their account
    with fields specified in variable 'fields', and changing the name that 
    customer sees while filling out the form, with name labeled in the variable 'labels',
    hence carries similar logic to creating a new user
    '''
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

    '''form to start selling an item, which appears when a new item will be listed,
    with fields specified in variable 'fields', no further changes needed regarding to names
    '''
     
    class Meta: 
        model = Item
        fields = [
            'title',
            'description',
            'price',
            'quantity_left'
            ]
        

class UpdateItemForm(forms.ModelForm):

    '''logic similar to CreateItemForm, which this will be updating an existing item,
    form structure is exactly the same, while the form will carry information that is filled
    depending on the current status of each item
      '''
    class Meta: 
        model = Item
        fields = [
            'title',
            'description',
            'price',
            'quantity_left'
            ]
        

class ChatMessageForm(forms.ModelForm):
    '''
    used when 2 people are sending messages, messages are allowed to carry information of message,
    which will be a piece of text with varying length, and also images along with the messages,
    labels variable changed the name of what the user sees, and widgets are to show a bit more hint
    to the 'message' field of the ChatMessage object, but it is not necessary to have the 'widgets' variable
    for this form to work
    '''
    class Meta:
        model = ChatMessage
        fields = ['message', 'image_self']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }
        labels = {
            'image_self': 'Add image'
        }
