# File: admin.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/19/2024
# Description: admin file for models


from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Customer) #register for profile 
admin.site.register(Item) #register for status message
admin.site.register(Order) #register for image, newly add @ oct.19
admin.site.register(Follower) #register for friend relationship added at oct24
admin.site.register(Image)
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
admin.site.register(ChatMessage)
admin.site.register(CustomerOrder)
admin.site.register(Notification)
