## hw/urls.py

from django.urls import path
from django.conf import settings
from . import views

#list of urls to have
urlpatterns = [
    path(r'', views.ShowAllView.as_view(), name='show_all'), # generic class-based view
]
