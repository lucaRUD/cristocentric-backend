from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20)
    bio = models.TextField()
    birth_date = models.DateField(null=True)

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_data = models.JSONField()

class Product(models.Model):
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    colors = models.JSONField()
    sizes = models.JSONField()
    description= models.CharField(max_length=512)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.URLField()