from django.urls import path
#from django.conf import settings
from . import views
#from django.contrib.auth import views as auth_views

app_name='marathon_analytics'

urlpatterns = [
    path(r'', views.ResultsListView.as_view(), name='home'), # generic class-based view
    path(r'results', views.ResultsListView.as_view(), name='results'),
    path(r'result/<int:pk>', views.ResultDetailView.as_view(), name='result_detail'),
]
