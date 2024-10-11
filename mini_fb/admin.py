from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Profile) #register for profile 
admin.site.register(StatusMessage) #register for status message
