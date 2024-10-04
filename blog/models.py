from django.db import models
#deinfe data models

# Create your models here.

class Article(models.Model):
    #attributes:

    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True) ##image field 

    def __str__(self):
        return f"{self.title} by {self.author}"


    


