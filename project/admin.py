# File: admin.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/09/2024
# Description: admin file for models


from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Customer) #register for Customer, for each user using the web, added @11/19
admin.site.register(Item) #register for Item, for each item being selling added @11/19
admin.site.register(Order) #register for Order, for each Order(item) that user placed, added@11/19, updated @12/4
admin.site.register(Follower) #register for Follower, for linking 2 users, added @11/23
admin.site.register(Image)#register for Image, for Images related to each item, added @11/19
admin.site.register(ShoppingCart)#register for ShoppingCart, for adding item into shopping cart, unique to each user, @11/24
admin.site.register(CartItem)#register for Cartitem, for each item in the shopping cart, added @11/24, updated@11/30
admin.site.register(ChatMessage)#register for ChatMessage, for messages sent between 2 people, added @11/25
admin.site.register(CustomerOrder) #register for CustomerOrder, for Customer placed order, added @12/3

admin.site.register(Notification) #register for Notification, for each item being placed(Item object)
#along with notification to the seller, added @12/4
