from django import forms
from .models import AuctionListing, Comment, Bid
from django.core.exceptions import ValidationError

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url']

    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2)

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['price']