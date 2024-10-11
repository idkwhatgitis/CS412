## hw/urls.py

from django.urls import path
from django.conf import settings
from . import views

app_name="blog"

#list of urls to have
urlpatterns = [
    path(r'', views.RandomArticleView.as_view(), name='random'), # generic class-based view
    path(r'show_all', views.ShowAllView.as_view(), name='show_all'),
    path(r'article/<int:pk>', views.ArticleView.as_view(), name='article'),
    path(r'article/<int:pk>/create_comment', views.CreateCommentView.as_view(), name='create_comment'),
]
