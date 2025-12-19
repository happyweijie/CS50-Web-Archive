from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

def index(request):
    auctions = Auction.objects.exclude(active=False).all()
    return render(request, "auctions/index.html", {
        "auctions": sorted(auctions, key=lambda a: a.id, reverse=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    if request.method == "GET":
        return render(request, "auctions/editor.html", {
            "categories": Category.objects.all(),
            "route": "new_listing",
        })
    else:
        # Ensure valid price is inputted
        try:
            price = float(request.POST.get("price"))
        except ValueError:
            messages.error(request, "Please enter a valid price")
            return HttpResponseRedirect(reverse("new_listing"))
        a = Auction(
            title=request.POST.get("title").strip(),
            description=request.POST.get("description").strip(),
            price=price,
            creator=request.user,
            category=Category.objects.get(id=int(request.POST.get("category"))),
            image=request.POST.get("image").strip()
        )
        a.save()
        return redirect(listing, a.id)
        

def listing(request, id):
    a = Auction.objects.get(pk=int(id))
    # Get information about bids
    bid_count = 0 if not a.bids.all() else len(a.bids.all())
    highest_bid = None if bid_count == 0 else sorted(a.bids.all(), key=lambda a: a.price, reverse=True)[0]

    # Check whether listing is in watchlist
    item_in_watchlist = None
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()
        item_in_watchlist = True if a in watchlist else False

    if not a.active and request.user == highest_bid.user:
        messages.info(request, f"You have won the auction at ${highest_bid.price}!!")

    return render(request, "auctions/listing.html", {
        "auction": a,
        "bid_count": bid_count,
        "highest_bid": highest_bid,
        "item_in_watchlist": item_in_watchlist,
        "comments": sorted(a.comments.all(), key=lambda a: a.id, reverse=True),
    })

@login_required
def watchlist(request):
    if request.method == "POST":
        user = User.objects.get(id=int(request.user.id))
        a = Auction.objects.get(pk=int(request.POST.get("auction_id")))
        if request.POST.get("action") == "add":
            user.watchlist.add(a.id)
        elif request.POST.get("action") == "remove":
            user.watchlist.remove(a.id)
        else:
            messages.error(request, "Error.")
            return HttpResponseRedirect(reverse("listing", args=(a.id,)))
        
        return HttpResponseRedirect(reverse("listing", args=(a.id,)))
    else:
        user = User.objects.get(pk=int(request.user.id))
        return render(request, "auctions/index.html", {
            "auctions": user.watchlist.all()
        })

@login_required
def bid(request):
    if request.method == "POST":
        try:
            mybid = float(request.POST.get("bid"))
        except ValueError:
            messages.error(request, "Please enter a valid price.")
            return HttpResponseRedirect(reverse("listing", args=(a.id,)))
        
        a = Auction.objects.get(pk=int(request.POST.get("auction_id")))

        # If bid is the first bid, ensure it is more than the starting price
        bid_count = 0 if not a.bids.all() else len(a.bids.all())
        if bid_count > 0:
            highest_bid = sorted(a.bids.all(), key=lambda a: a.price, reverse=True)[0]

        if bid_count == 0 and mybid < a.price:
            messages.error(request, "Please ensure that your bid is greater than or equal to the starting bid.")
            return HttpResponseRedirect(reverse("listing", args=(a.id,)))
        elif bid_count > 0 and highest_bid.price > mybid:
            messages.error(request, "Please ensure that your bid is greater than or equal to the current bid.")
            return HttpResponseRedirect(reverse("listing", args=(a.id,)))
        
        bid = Bid(
            auction=a,
            user=request.user,
            price=mybid,
        )
        bid.save()

        messages.success(request, "Your bid has been placed!")
        return HttpResponseRedirect(reverse("listing", args=(a.id,)))


@login_required
def close(request):
    a = Auction.objects.get(pk=int(request.POST.get("auction_id")))
    highest_bid = sorted(a.bids.all(), key=lambda a: a.price, reverse=True)[0]
    highest_bid.acceptance = True
    highest_bid.save()
    a.active = False
    a.save()
    messages.success(request, f"{highest_bid.user.username} has won the auction!")
    return HttpResponseRedirect(reverse("listing", args=(a.id,)))


def categories(request):
    if request.method == "GET":
        return render(request, "auctions/categories_search.html", {
            "categories": Category.objects.all(),
        })
    

def results(request):
    category = Category.objects.get(pk=int(request.GET.get("category")))
    return render(request, "auctions/index.html", {
        "auctions": sorted(category.auctions.exclude(active=False).all(), key=lambda a: a.id, reverse=True)
    })


@login_required
def comment(request):
    if request.method == "POST":
        a = Auction.objects.get(pk=int(request.POST.get("auction_id")))
        text = request.POST.get("comment").strip()
        c = Comment(
            auction=a,
            user=request.user,
            text=text,
        )
        c.save()
        return HttpResponseRedirect(reverse("listing", args=(a.id,)))


def users(request, id):
    user = User.objects.get(pk=int(id))
    return render(request, "auctions/index.html", {
        "auctions": user.myauctions.exclude(active=False).all()
    })
