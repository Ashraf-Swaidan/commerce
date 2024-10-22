from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CreateListingForm,AddCommentForm,BidForm
from .models import AuctionListing,Bid,Comment,Category,Watchlist
from django.db.models import Max
from django.contrib import messages


from .models import User


def index(request):
    return render(request, "auctions/index.html")

def login_view(request):
    if request.method == "POST":

        # A humble attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Checking if authentication turned out to be successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("active_listings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("active_listings"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensuring password matches the confirmation field as well
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempting to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            watchlist = Watchlist(user=user)
            watchlist.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("active_listings"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'GET':
        form = CreateListingForm(initial={
            'title': '',
            'description': '',
            'starting_bid': '',
            'image_url':'',
            'category':'',
        })
    else:
        form = CreateListingForm(request.POST)
        if(form.is_valid()):
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()

            watchlist = Watchlist.objects.get(user=request.user)
            watchlist.listing.add(listing)

            return redirect('listing_details', listing_id=listing.id)
        
    return render(request, 'auctions/create_listing.html', {'form':form})

def active_listings(request):
    active_listings = AuctionListing.objects.filter(isActive=True)
    
    # Initialize highest_bid as None or 0, depending on your requirements
    highest_bid = None 

    for listing in active_listings:
        # Calculate highest_bid for each listing
        listing.highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('price'))['price__max']
        # You can also set highest_bid for overall context if needed
        if listing.highest_bid is not None:  # Only update if it has a value
            highest_bid = max(highest_bid or 0, listing.highest_bid)  # Update the highest overall bid

    return render(request, 'auctions/index.html', {
        'active_listings': active_listings, 'highest_bid': highest_bid
    })


def listing_details(request,listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)
    watchlisted = Watchlist.objects.filter(user=request.user, listing = listing).exists() if request.user.is_authenticated else False
    bid_form = BidForm()
    comment_form = AddCommentForm(initial={'content':''})
    
    add_comment(request,listing_id)


    highest_bid = bids.aggregate(Max('price'))['price__max']
    listing.highest_bid = highest_bid
    
    if listing.isActive != True:
        winning_bid = bids.order_by('-price').first()
        
    else:
        winning_bid = None
        
    content = {
        'listing': listing,
        'bids': bids,
        'comments':comments,
        'watchlisted':watchlisted,
        'bid_form': bid_form,
        'winning_bid':winning_bid,
        'comment_form':comment_form
    }

    return render(request, 'auctions/listing_details.html',content)


def place_bid(request, listing_id):
    if request.user.is_authenticated:

        if not AuctionListing.objects.get(pk=listing_id).isActive:
            return redirect('listing_details',listing_id=listing_id)
        
        if request.method == 'POST':
            form = BidForm(request.POST)
            if form.is_valid():
                bid = form.save(commit=False)
                bid.user = request.user
                bid.listing = AuctionListing.objects.get(pk=listing_id)

                starting_bid = bid.listing.starting_bid

                highest_bid = Bid.objects.filter(listing=bid.listing).order_by('-price').first()

                if (highest_bid is None and bid.price>= starting_bid) or (highest_bid is not None and bid.price>highest_bid.price):
                    bid.save()

                    #Adding listing to the watchlist to let the buddy keep track of the listings he participated in.

                    watchlist = Watchlist.objects.get(user=request.user)
                    watchlist.listing.add(bid.listing)
                else:
                    #Adding Error messages
                    if(highest_bid is None and bid.price<starting_bid):
                        messages.error(request, "Bid should be equal or greater than the starting bid : " + str(starting_bid))
                    elif(highest_bid is not None and bid.price<=highest_bid.price):
                        messages.error(request, "Bid should be greater than the highest ongoing bid: " + str(highest_bid.price))

        
        return redirect('listing_details', listing_id=listing_id)
    
    return redirect('login')

def close_auction(request, listing_id):
    if request.user.is_authenticated:
        listing = AuctionListing.objects.get(pk=listing_id)

        if request.user == listing.owner and listing.isActive:
                listing.isActive = False
                listing.save()
              

    return redirect('listing_details', listing_id=listing_id)

def add_comment(request, listing_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.listing = AuctionListing.objects.get(pk=listing_id)
                comment.save()
                return redirect('listing_details', listing_id=listing_id)

    else:
        if request.method == 'POST':
            return redirect('login')
        
    return redirect('listing_details', listing_id=listing_id)
        



def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    active_listings = AuctionListing.objects.filter(category=category, isActive=True)
    highest_bid = None
    for listing in active_listings:
        if(listing):
            highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('price'))['price__max']
            listing.highest_bid = highest_bid
        else:
            highest_bid = None
    return render(request, 'auctions/category_listings.html', {'category':category, 'active_listings': active_listings, 'highest_bid': highest_bid})



def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/all_categories.html', {
        'categories':categories
    })


def watchlist(request):
    if request.user.is_authenticated:
            watchlist = Watchlist.objects.get(user=request.user)
            listings = watchlist.listing.all()

        # Fetching the highest bids for each listing and storing them in a dictionary
            if listings:
                for listing in listings:
                    highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('price'))['price__max']
                    listing.highest_bid = highest_bid
            else:
                highest_bid = None
            return render(request, 'auctions/watchlist.html', {'watchlist': watchlist, 'listings':listings,'highest_bid':highest_bid})
    
    return redirect('login')



def unwatchlist(request,listing_id):
    if request.user.is_authenticated:
       watchlist = Watchlist.objects.get(user=request.user)
       listing = AuctionListing.objects.get(pk=listing_id)
       watchlist.listing.remove(listing)
    return redirect('watchlist')

def toggle_watchlist(request, listing_id):
    if request.user.is_authenticated:
        listing = AuctionListing.objects.get(pk=listing_id)
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        
        if listing in watchlist.listing.all():
            watchlist.listing.remove(listing)
        else:
            watchlist.listing.add(listing)
    
    return redirect('listing_details', listing_id=listing_id)

