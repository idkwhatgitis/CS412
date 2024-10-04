from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path(r'', views.ShowAllProfilesView.as_view(), name='show_all'), # generic class-based view
]