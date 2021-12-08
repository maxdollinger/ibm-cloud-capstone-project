from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealers_by_state, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    context['title'] = 'About us'
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    context['title'] = 'Contact us'
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    context['title'] = 'Dealership'
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf()
        context['dealerships'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    context['title'] = 'Dealership Details'
    if request.method == "GET":
        context['dealership'] = get_dealer_by_id_from_cf(dealer_id)
        context['reviews'] = get_dealer_reviews_from_cf(dealer_id)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        context['dealer_id'] = dealer_id
        context['username'] = request.user.first_name + " " + request.user.last_name
        context['cars'] = CarModel.objects.all()

        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        car_id = request.POST.get('car')
        car = CarModel.objects.get(id=car_id)
        purchase = request.POST.get('purchase')

        review = {}
        review['time'] = datetime.utcnow().isoformat().split('T')[0]
        review['dealership'] = dealer_id
        review['review'] = request.POST.get('review')
        review['name'] = request.POST.get('username')
        review['purchase_date'] = request.POST.get('purchasedate')
        review['car_model'] = car.name
        review['car_year'] = car.year.year
        review['car_make'] = car.carmake.name

        if purchase == 'on':
            review['purchase'] = True
        else:
            review['purchase'] = False

        if request.user and request.user.is_authenticated:
            json_payload = { "review": review }
            post_request('https://2e35c4b8.eu-gb.apigw.appdomain.cloud/api/review', json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id)
        else:
            return redirect("djangoapp:dealer_details", dealer_id)

