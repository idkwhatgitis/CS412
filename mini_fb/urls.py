from django.urls import path
from django.conf import settings
from . import views

app_name='mini_fb'

urlpatterns = [
    path(r'', views.ShowAllProfilesView.as_view(), name='show_all'), # generic class-based view
    path(r'profiles/<int:pk>', views.ShowProfilePageView.as_view(), name='show_profile'), #profile detail view
    path(r'create_profile', views.CreateProfileView.as_view(), name='create_profile'), #forms to create a profile
    path(r'profiles/<int:pk>/create_status', views.CreateStatusMessageView.as_view(), name='URL_create_status'), #creating a message

]





