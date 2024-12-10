# File: urls.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/08/2024
# Description: url patterns for different pages

from django.urls import path
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

app_name='project'

urlpatterns = [
    path('', views.ShowAllItemView.as_view(), name='show_all'), #base view
    path('item/<int:pk>/', views.ShowDetailItemView.as_view(), name='show_detail'), #details of each item and some info about seller
    path('user/<int:pk>/', views.ShowUserPageView.as_view(), name="show_user"), #user profile view, can be accessed even if user did not login
    path('user/', views.ShowUserSelfView.as_view(), name="show_self"), #user self view, only available to the user itself and cannot be accessed by other, since this allows update of account info and selling/updating/deleting an item 
    path('logout/', auth_views.LogoutView.as_view(template_name='project/logout.html'), name='logout'), #logout view for every user
    path('cart/', views.ShowCartView.as_view(), name='shopping_cart'), #shopping cart of the user, contains items that user has added, allows update/delete
    path('create_user/', views.CreateCustomerView.as_view(), name='create_customer'), #used when registration of a new user
    path('add_to_cart/<int:item_pk>/add/', views.AddToCartView.as_view(), name='add_to_cart'), #adding an item to the shopping cart of the user
    path('login/', views.CustomLoginView.as_view(), name='login'), #login page for every user, asking for correct username and password combination
    path('customer/update/', views.UpdateCustomerView.as_view(), name='update_account'), #updating account info, can be accessed in ShowUserSelfView as a button
    path('add_follower/<int:customer_pk>/', views.AddFollowerView.as_view(), name='add_follower'), #enable following of one user to the aother, which creates a Follower object
    path('followings/', views.FollowingsListView.as_view(), name='following_list'), #check who the user is following, shown as a ist
    path('followers/', views.FollowersListView.as_view(), name='follower_list'), #check who is the follower of the user, shown as a list
    path('chats/', views.ChatListView.as_view(), name='chat_list'), #see who the user has sent message or someone has sent the message to the user, and contains chat history
    path('chats/<int:customer_pk>/', views.ChatDetailView.as_view(), name='chat_detail'), #chat page between 2 users, can be accessed from the ChatListView
    path('item/create/', views.CreateItemView.as_view(), name='create_item'), #creating a new item to sell, to be accessed in ShowUserSelfView(you have to be the user to sell an item)
    path('item/update/<int:pk>/', views.UpdateItemView.as_view(), name='update_item'), #updating an item, can be accessed in ShowUserSelfView for each user's item
    path('cart/checkout/', views.CheckoutCartView.as_view(), name='checkout_cart'), #checkout for the cart, user can select item to checkout
    path('notifications/', views.NotificationListView.as_view(), name='notification'), #list of notification, which notifies the seller who bought an item
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'), #order detail from notification, for each notification, we can see the detail of the order
    path('pastorder/', views.PastOrdersView.as_view(), name='past_order'), # list of orders for each user has placed
    path('notifications/mark_as_read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),#mark the notification as read, so the red dot on Notifications link  dissappears
    path('item/<int:pk>/delete/', views.DeleteItemView.as_view(), name='delete_item'), #deleting an item for the user, in other words, stop selling it
    path('graphs', views.StatisticsView.as_view(), name='graph'), #graphs for the web application
   ]





