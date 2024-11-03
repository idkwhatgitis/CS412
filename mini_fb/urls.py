# File: urls.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/1/2024
# Description: url patterns for different pages

from django.urls import path
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

app_name='mini_fb'

urlpatterns = [
    path(r'', views.ShowAllProfilesView.as_view(), name='show_all'), # generic class-based view
    path(r'profile/<int:pk>', views.ShowProfilePageView.as_view(), name='show_profile'), #profile detail view
    path(r'create_profile', views.CreateProfileView.as_view(), name='create_profile'), #forms to create a profile
    path(r'status/create_status', views.CreateStatusMessageView.as_view(), name='URL_create_status'), #creating a message
    path(r'profile/update', views.UpdateProfileView.as_view(), name='update_profile'), #updating profile
    path(r'status/<int:pk>/delete', views.DeleteStatusMessageView.as_view(), name='delete_message'), #deleting statue message
    path(r'profile/<int:pk>/update_message', views.UpdateStatusMessageView.as_view(), name='update_message'), #updating status message
    path(r'profile/add_friend/<int:other_pk>', views.CreateFriendView.as_view(), name='add_friend'), #creating friend view
    path(r'profile/friend_suggestions', views.ShowFriendSuggestionsView.as_view(), name='friend_suggestions'), #view friend suggestions
    path(r'profile/news_feed', views.ShowNewsFeedView.as_view(), name='news_feed'), #view news feed related to that person

    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'), #logging in
    path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout'), #logging out 
]





