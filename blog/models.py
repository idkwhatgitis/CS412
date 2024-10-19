from django.db import models
from django.urls import reverse
#deinfe data models

# Create your models here.

class Article(models.Model):
    #attributes:

    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    ## image_url = models.URLField(blank=True) ##image field 
    image_fil = models.ImageField(blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_comments(self):
        '''get all the comments related to this article'''
        comments = Comment.objects.filter(article=self)
        return comments
    
    def get_absolute_url(self):
        "returning url to view one instance of object"
        #pk = self.pk primary key of this object
        return reverse('blog:article', kwargs={'pk': self.pk})

        
class Comment(models.Model):
    'comment of articles'

    article = models.ForeignKey("Article", on_delete = models.CASCADE)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)

    def __str__(self):
        'return a string representation of object'
        return f'{self.text}'

    

    


