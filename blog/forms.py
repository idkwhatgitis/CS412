from django import forms
from .models import Comment, Article

class CreateCommentForm(forms.ModelForm):
    '''forms for adding another comment'''

    class Meta:
        model = Comment
        fields = ['author', 'text'] #fields to include in the form


class CreateArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['author', 'title', 'text', 'image_fil']