from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    isActive = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} bid {self.price} on {self.listing.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.user.username} commented on {self.listing.title}"
    
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField((AuctionListing))

    def __str__(self):
        return f"{self.user.username}'s watchlist"
