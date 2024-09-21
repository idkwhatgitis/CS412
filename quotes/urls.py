

from django.urls import path
from django.conf import settings
from . import views
from django.templatetags.static import static


#list of urls to have
urlpatterns = [
    path(r'', views.quote, name="quote"),#name is same as the name of views
    path(r'about', views.about, name="about"),
    path(r'show_all', views.show_all, name="show_all"),
    #must have the r before ''
    #path(url, view, name)
    
]
