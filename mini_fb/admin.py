# File: admin.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/11/2024
# Description: admin file for models


from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Profile) #register for profile 
admin.site.register(StatusMessage) #register for status message
