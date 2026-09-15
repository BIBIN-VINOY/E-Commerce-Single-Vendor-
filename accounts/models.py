from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(
        default='images/default-profile.png',
        upload_to="profiles/",
        blank=True,
        null=True
    )


    def __str__(self):
        return self.username
    
class Address(models.Model):

    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('office', 'Office'),
    )
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPES,
        default='home'
    ) 

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )


    full_name = models.CharField(max_length=100)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.address_type}"
    


