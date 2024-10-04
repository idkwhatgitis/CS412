from django.db import models

# Create your models here.


class Profile(models.Model):
    #attributes:

    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    image_url = models.URLField(blank=True) ##image field 

    def __str__(self):
        return f"{self.first_name} by {self.last_name} by {self.city} by {self.email_address}"
