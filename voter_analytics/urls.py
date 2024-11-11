# File: urls.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/10/2024
# Description: urls for each page


from django.urls import path
from . import views

app_name='voter_analytics'

urlpatterns = [
    path(r'', views.VotersListView.as_view(), name='home'), # generic class-based view
    path(r'voters', views.VotersListView.as_view(), name='results'), # list view of voters
   path(r'voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'), #detail page
    path(r'graphs', views.GraphDetailView.as_view(), name='graph'), #graphs analytics
]
