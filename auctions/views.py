from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Bids, Comments, Items, User 


class CreateItem(forms.Form):
    title = forms.CharField(label="Title", max_length=64, required=True)
    description = forms.CharField(label="Description", max_length=350, required=True, widget=forms.Textarea)
    image_url = forms.URLField(label="ImageURL", required=False)
    price = forms.FloatField(label="Price", min_value=0.00, required=True)
    category = forms.CharField(label="Category", max_length=64, required=False)


def index(request):
    return render(request, "auctions/index.html", {
        "items": Items.objects.filter(is_active=True)
    })


def category(request, category):
    pass


def item(request, item):
    pass


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

            items = Items(
                title=title,
                description=description,
                price=price,
                image_url=image_url,
                category=category,
                owner=request.user
            )
            items.save()

        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        form = CreateItem()
            
    return render(request, "auctions/create.html", {
            "form": form
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
