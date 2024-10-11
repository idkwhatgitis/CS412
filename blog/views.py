from django.shortcuts import render
from .models import Article

from django.views.generic import ListView, DetailView, CreateView
from .forms import *

from typing import Any
from django.urls import reverse

import random

class ShowAllView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''
    model = Article # retrieve objects of type Article from the database
    template_name = 'blog/show_all.html'
    context_object_name = 'articles'  ##read the object from databse(entirely!, all attributes)


class RandomArticleView(DetailView):
    "show article selected at random"
    model= Article
    template_name = 'blog/article.html'
    context_object_name = 'article'

    def get_object(self):
        '''return instance of article'''
        all_articles = Article.objects.all()

        return random.choice(all_articles)


class ArticleView(DetailView):
    "show article selected at random"
    model= Article
    template_name = 'blog/article.html'
    context_object_name = 'article'

    
class CreateCommentView(CreateView):
    '''A view to create comments on article
        on get: send back the for for dispay
        on post: rewad/process the form and save it to the DB
    '''

    form_class = CreateCommentForm
    template_name = "blog/create_comment_form.html"

    def get_context_data(self, **kwargs:Any) -> dict[str, Any]:

        #get the context data
        context = super().get_context_data(**kwargs)
        article = Article.objects.get(pk=self.kwargs['pk'])
        context['article'] = article
        return context

    def get_success_url(self) -> str:
        article = Article.objects.get(pk=self.kwargs['pk'])
        return reverse('blog:article', kwargs=self.kwargs)

    def form_valid(self, form):
        ###self.kwargs shows the pk, form.cleane_data shows the fields with its argument
        article = Article.objects.get(pk=self.kwargs['pk'])

        #attach the article to the instance of cmoment
        form.instance.article = article

        return super().form_valid(form)
        