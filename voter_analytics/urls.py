from django.urls import path
#from django.conf import settings
from . import views
#from django.contrib.auth import views as auth_views

app_name='voter_analytics'

urlpatterns = [
    path(r'', views.VotersListView.as_view(), name='home'), # generic class-based view
    path(r'voters', views.VotersListView.as_view(), name='results'),
   path(r'voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'),
    path(r'graphs', views.GraphDetailView.as_view(), name='graph'),
]
