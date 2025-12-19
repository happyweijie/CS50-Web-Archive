from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
    pass


class Category(models.Model):
    type = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}: {self.type}"


class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="myauctions")
    interested_viewers = models.ManyToManyField(User, blank=True, default=None, related_name="watchlist")
    category = models.ForeignKey(Category, default=1, on_delete=models.SET_DEFAULT, related_name="auctions")
    image = models.URLField(max_length=200, blank=True)
    publish_time = models.DateTimeField(default=datetime.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user.username} posted {self.text} on {self.auction.title}."


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="bids")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    acceptance = models.BooleanField(default=False)

    def __str__(self):
        status = "accepted" if self.acceptance else "not accepted"
        return f"{self.price} for {self.auction.title} by {self.user.username} is {status}"
