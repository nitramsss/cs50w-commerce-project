from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import Bid, Comment, Item, User 

class CreateItem(forms.Form):
    title = forms.CharField(
        label="Item Title",
        max_length=64,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter the title of the item",
        }),
    )

    description = forms.CharField(
        label="Description",
        max_length=350,
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter a detailed description of the item",
            "rows": 4,
        }),
    )

    image_url = forms.URLField(
        label="Image URL",
        required=False,
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "Enter a URL for the item image (optional)",
        }),
    )

    price = forms.FloatField(
        label="Price (USD)",
        min_value=0.00,
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter the price of the item",
        }),
    )

    category = forms.CharField(
        label="Category",
        required=True,
      widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter category",
        }))


    def clean_title(self):
        title = self.cleaned_data["title"]
        if Item.objects.filter(title=title).exists():
            raise forms.ValidationError("An item with this title already exists.")
        return title


class CommentForm(forms.Form):
    comment = forms.CharField(
            label="Add Your Comment",
            max_length=500,
            required=False,
            widget=forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'Write your comment here...',
                    'rows': 5,  
                    'style': 'resize: none;', 
                }
            )
        )    
    

class BiddingForm(forms.Form):
    bid = forms.FloatField(
        label="Your Bid",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your bid',
            'min': '0',  # Ensure positive numbers
            'step': '0.01'  # Allow decimal bids
        })
    )
    item_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )

    def check_bid(self):
        bid = self.cleaned_data["bid"]
        item_id = self.cleaned_data["item_id"]
        item = Item.objects.filter(pk=item_id).first()
        if item and bid <= item.price:
            raise forms.ValidationError(
                "Bid must be higher than the initial price and current highest bid."
            )
        return bid


def index(request):
    return render(request, "auctions/index.html", {
        "items": Item.objects.filter(is_active=True)
    })


def category(request):
    all_categories = Item.objects.values("category").distinct()

    return render(request, "auctions/category.html", {
        "categories": all_categories
    })


def items_in_category(request, category):
    all_categories = Item.objects.values("category").distinct()

    return render(request, "auctions/category.html", {
        "categories": all_categories,
        "items": Item.objects.filter(category=category)
    })


@login_required
def add_watchlist(request, item_id):
    user = request.user
    user.watchlist.add(item_id)
    user.save()
                       
    return HttpResponseRedirect(reverse('watchlist'))


@login_required
def remove_watchlist(request, item_id):
    user = request.user
    user.watchlist.remove(item_id)
    user.save()
                       
    return HttpResponseRedirect(reverse('watchlist'))


@login_required
def watchlist(request):
    item_ids = request.user.watchlist.values_list('id', flat=True)
    items = Item.objects.filter(id__in=item_ids)

    return render(request, "auctions/watchlist.html", {
        "items": items
    })


@login_required
def comment(request, item_id):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.cleaned_data["comment"]
            commenter = request.user
            item_commented = Item.objects.get(pk=item_id)

            c = Comment(
                comment=comment,
                commenter=commenter,
                item_commented=item_commented
            )
            c.save()
    
    return HttpResponseRedirect(reverse('item', args=[item_id]))


@login_required
def bidding(request, item_id):
    item = Item.objects.get(pk=item_id)

    if request.method == "POST":
        bidding_form = BiddingForm(request.POST)

        if bidding_form.is_valid():
           pass
        else:
            return render(request, "auctions/item.html", {
                "message": "Bid must be higher than the current price of the item"
            })
    return HttpResponseRedirect(reverse('item', args=[item_id]))


@login_required
def close_item(request, item_id, bidder_id):

    bid = Bid.objects.get(pk=item_id)
    item = Item.objects.get(pk=item_id)
    
    item.is_active = False
    item.save()


    
    item.owner = bid.bidder
    
    return HttpResponseRedirect(reverse('item', args=[item_id]))
        

@login_required
def item(request, item_id):
    """Show the item details"""
    # Get the highest bid and details of the item
    item = Item.objects.get(pk=item_id)
    highest_bid = Bid.objects.filter(item_bid=item).order_by('-bid').first()
    bidder = highest_bid.bidder if highest_bid else None
    
    bid_count = Bid.objects.filter(item_bid=item).count()    
    message = None

    in_watchlist = request.user.watchlist.filter(pk=item_id).exists()

    # Assign the price for the item
    if highest_bid and float(item.price) < float(highest_bid.bid):
        item.price = float(highest_bid.bid)
        item.save()
    
    bidding_form = BiddingForm()
    comment_form = CommentForm()

    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            bidder = request.user
            item_bid = item

            
            if float(bid) >= item.price and not Bid.objects.filter(item_bid__pk=item_id).exists():
                b = Bid(
                    bid=float(bid),
                    bidder=bidder,
                    item_bid=item_bid
                )
                b.save()    

                item.price = float(bid)
                item.save()

                bid_count = Bid.objects.filter(item_bid=item).count()    

                message = "Bid successfully!"
            elif float(bid) > item.price:
                b = Bid(
                    bid=float(bid),
                    bidder=bidder,
                    item_bid=item_bid
                )
                b.save()   

                item.price = float(bid)
                item.save()

                bid_count = Bid.objects.filter(item_bid=item).count()    

                message = "Bid successfully!"
            else:
                message = "Bid must be higher than the current price of the item."

        else:
            bidding_form = BiddingForm()

    return render(request, "auctions/item.html", {
        "comment_form": comment_form,
        "bidding_form": bidding_form,
        "message": message,
        "watchlist": in_watchlist,
        "item": item,
        "bid_count": bid_count,
        "comments": Comment.objects.filter(item_commented=item_id)
    })



@login_required
def create(request):
    # If method is post get item inputs
    if request.method == 'POST':
        form = CreateItem(request.POST)

        # If input is valid then record it otherwise render html form
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image_url = form.cleaned_data["image_url"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]

            item = Item(
                title=title,
                description=description,
                price=price,
                image_url=image_url,
                category=category,
                owner=request.user
            )
            item.save()
            
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": CreateItem()
            })
            
    return render(request, "auctions/create.html", {
            "form": CreateItem()
        })


        # Check if item is in watchlist


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
