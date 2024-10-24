# File: urls.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 10/19/2024
# Description: url patterns for different pages

from django.urls import path
from django.conf import settings
from . import views

app_name='mini_fb'

urlpatterns = [
    path(r'', views.ShowAllProfilesView.as_view(), name='show_all'), # generic class-based view
    path(r'profiles/<int:pk>', views.ShowProfilePageView.as_view(), name='show_profile'), #profile detail view
    path(r'create_profile', views.CreateProfileView.as_view(), name='create_profile'), #forms to create a profile
    path(r'profiles/<int:pk>/create_status', views.CreateStatusMessageView.as_view(), name='URL_create_status'), #creating a message
    path(r'profiles/<int:pk>/update', views.UpdateProfileView.as_view(), name='update_profile'), #updating profile
    path(r'profiles/<int:pk>/delete', views.DeleteStatusMessageView.as_view(), name='delete_message'), #deleting statue message
    path(r'profiles/<int:pk>/update_message', views.UpdateStatusMessageView.as_view(), name='update_message'), #updating status message
    path(r'profiles/<int:pk>/add_friend/<int:other_pk>', views.CreateFriendView.as_view(), name='add_friend'), #creating friend view
    path(r'profiles/<int:pk>/friend_suggestions', views.ShowFriendSuggestionsView.as_view(), name='friend_suggestions'), #view friend suggestions
    path(r'profiles/<int:pk>/news_feed', views.ShowNewsFeedView.as_view(), name='news_feed'), #view news feed related to that person
]





