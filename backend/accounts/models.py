from django.db import models
from django.contrib.auth.models import AbstractUser

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    general_location = models.CharField(default='City,Country',max_length=100)
    image = models.ImageField(upload_to='images/',default='images/noimage.jpg',null=True, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateField(auto_now_add=True)
    is_public= models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    organizer = models.ForeignKey("CustomUser", on_delete=models.CASCADE)


    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M')

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20)
    bio = models.TextField()
    birth_date = models.DateField(null=True)
    saved_events = models.ManyToManyField(Event, blank=True, related_name='users_saved')


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    prodigi_order_id = models.CharField(max_length=255)
    order_data = models.JSONField()

class Product(models.Model):
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    colors = models.JSONField()
    sizes = models.JSONField()
    description= models.CharField(max_length=512)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.URLField()


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to='images/',default='images/noimage.jpg', null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_public = models.BooleanField (default=False)

