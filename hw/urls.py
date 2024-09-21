## hw/urls.py

from django.urls import path
from django.conf import settings
from . import views

#list of urls to have
urlpatterns = [
    path(r'', views.home, name="home"),#name is same as the name of views
    path(r'about', views.about, name="about"),
    #must have the r before ''
    #path(url, view, name)
    
]
