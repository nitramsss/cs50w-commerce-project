from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    watchlist = models.ManyToManyField('Item', blank=True, related_name="watchlisted_by")

    def __str__(self):
        return f"{self.username}"


class Item(models.Model):
    title = models.CharField(max_length=64, unique=True, null=False)
    description = models.TextField(max_length=350, null=False)
    price = models.FloatField(default=0.00, blank=False)
    image_url = models.URLField(blank=False, null=False)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.FloatField(default=0.00, null=False, validators=[MinValueValidator(0.01)])
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    item_bid = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bid}, {self.bidder}, {self.item_bid}"  


class Comment(models.Model):
    comment = models.TextField(max_length=500, blank=True, null=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    item_commented = models.ForeignKey(Item, on_delete=models.CASCADE)
    date_commented = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"{self.comment}"
    