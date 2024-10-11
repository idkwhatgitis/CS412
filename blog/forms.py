from django import forms
from .models import Comment

class CreateCommentForm(forms.ModelForm):
    '''forms for adding another comment'''

    class Meta:
        model = Comment
        fields = ['author', 'text'] #fields to include in the form

