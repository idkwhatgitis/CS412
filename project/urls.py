# File: urls.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/1/2024
# Description: url patterns for different pages

from django.urls import path
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

app_name='project'

urlpatterns = [
    path('', views.ShowAllItemView.as_view(), name='show_all'),
    path('item/<int:pk>/', views.ShowDetailItemView.as_view(), name='show_detail'),
    path('user/<int:pk>/', views.ShowUserPageView.as_view(), name="show_user"),
    path('user/', views.ShowUserSelfView.as_view(), name="show_self"),
    path('logout/', auth_views.LogoutView.as_view(template_name='project/logout.html'), name='logout'),
    path('cart/', views.ShowCartView.as_view(), name='shopping_cart'),
    path('create_user/', views.CreateCustomerView.as_view(), name='create_customer'),
    path('add_to_cart/<int:item_pk>/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('customer/update/', views.UpdateCustomerView.as_view(), name='update_account'),
    path('add_follower/<int:customer_pk>/', views.AddFollowerView.as_view(), name='add_follower'),
    path('followings/', views.FollowingsListView.as_view(), name='following_list'),
    path('followers/', views.FollowersListView.as_view(), name='follower_list'),
    path('chats/', views.ChatListView.as_view(), name='chat_list'),
    path('chats/<int:customer_pk>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('item/create/', views.CreateItemView.as_view(), name='create_item'),
    path('item/update/<int:pk>/', views.UpdateItemView.as_view(), name='update_item'),
    path('cart/checkout/', views.CheckoutCartView.as_view(), name='checkout_cart'),
    path('notifications/', views.NotificationListView.as_view(), name='notification'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('pastorder/', views.PastOrdersView.as_view(), name='past_order'),
    path('cart/delete_multiple/', views.DeleteCartItemsView.as_view(), name='delete_cart_items'),
    path('notifications/mark_as_read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('item/<int:pk>/delete/', views.DeleteItemView.as_view(), name='delete_item'),
   ]





