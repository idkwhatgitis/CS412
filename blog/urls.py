## hw/urls.py

from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views

app_name="blog"

#list of urls to have
urlpatterns = [
    path(r'', views.RandomArticleView.as_view(), name='random'), # generic class-based view
    path(r'show_all', views.ShowAllView.as_view(), name='show_all'),
    path(r'article/<int:pk>', views.ArticleView.as_view(), name='article'),
    path(r'article/<int:pk>/create_comment', views.CreateCommentView.as_view(), name='create_comment'),
    path(r'create_article', views.CreateArticleView.as_view(), name='create_article'),
    #for authentication
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='blog:show_all'), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),

]
