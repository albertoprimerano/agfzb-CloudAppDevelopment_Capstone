from datetime import datetime
import logging

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import render
from django.urls import reverse

from .models import CarModel, CarReview
from .restapis import get_dealer_review_from_cf, get_dealers_from_cf, get_dealers_by_id, post_request
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

ibm_cloud_url = "https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/"
ibm_cloud_api = "api/66c2d60e7b2effc7b7c0cfad382d7057e14842b53713bc3a4b238b33266e5067/"

post_review_api = "dealership_api/post_review"
get_reviews_api = "dealership_api/get_reviews"
get_dealerships_api = "dealership_api/get_dealerships"


# Render about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Render contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')


# Handle customer login request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return render(request, 'djangoapp/index.html')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


# Handle customer logout request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    context = {}
    # Redirect user back to course list view
    return render(request, 'djangoapp/index.html')


# Handle customer registration request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/user_registration.html', context)


# Handle get dealership requests
def get_dealerships(request):
    # If it is a GET request, load dealers using a restapi function an render the index page
    if request.method == "GET":
        url = ibm_cloud_url + ibm_cloud_api + get_dealerships_api
        # Get dealers from the URL passing no parameters to get all the results
        dealerships = get_dealers_from_cf(url)
        dealership_list = []
        for element in dealerships:
            dealership_list.append(element)
        context = {"dealership_list": dealership_list}
        return render(request, 'djangoapp/index.html', context)


# Handle dealer details requests (request a dealer_id)
def get_dealer_details(request, dealer_id, dealer_full_name):
    # If it is a GET request, load dealers using a restapi function an render the index page
    if request.method == "GET":
        url = ibm_cloud_url + ibm_cloud_api + get_reviews_api
        # Get dealers from the URL passing dealer_id to get the specific dealer details
        reviews = get_dealer_review_from_cf(url, dealer_id)
        review_list = []
        for review in reviews:
            review_list.append(review)
        context = {"review_list": review_list, "dealer_id": dealer_id, "dealer_full_name": dealer_full_name}
        return render(request, 'djangoapp/dealer_details.html', context)


# Handle add review requests (request a dealer_id)
def add_review(request, dealer_id, dealer_full_name):
    # If it is a GET request, load details and display add review page
    if request.method == "GET":
        # get the cars details for the specific dealer id
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        # set the context
        context = {"dealer_id": dealer_id, "dealer_full_name": dealer_full_name, "cars": cars}
        # render the page
        return render(request, 'djangoapp/add_review.html', context)
    # If it is a POST request, save the review and then redirect to the detail page
    if request.method == "POST" and request.user.is_authenticated:
        review = dict()
        # Set the message
        review["review"] = request.POST["content"]
        # Set Purchase flag to True or False
        if "purchasecheck" in request.POST:
            review["purchase"] = True
        else:
            review["purchase"] = False
        # Set the reviewer name
        if not request.user.first_name and not request.user.last_name:
            review["name"] = request.user.first_name + " " + request.user.last_name
        else:
            review["name"] = request.user.username
        car = CarModel.objects.get(id=request.POST["car"])
        # Set the car related information
        review["car_model"] = car.name
        review["car_make"] = car.car_make.name
        review["car_year"] = car.year.strftime("%Y")
        # Set another flag to emtpy (not sure wht is this about)
        review["another"] = ""
        # Set the purchase date
        review["purchase_date"] = request.POST["purchasedate"]
        get_url = ibm_cloud_url + ibm_cloud_api + get_dealerships_api

        review_list = get_dealer_review_from_cf(get_url, dealer_id="")
        # Calculate the maximum id to define
        id_to_use = 0
        for review in review_list:
            if review.id > id_to_use:
                id_to_use = review.id
        review["id"] = id_to_use + 1
        # Set the dealership to the dealer ID
        review["dealership"] = dealer_id

        json_payload = dict()
        json_payload["review"] = review
        post_url = ibm_cloud_url + ibm_cloud_api + post_review_api
        response = post_request(post_url, json_payload=json_payload)
        return redirect(
            reverse('djangoapp:dealer_details', kwargs={'dealer_id': dealer_id, 'dealer_full_name': dealer_full_name}))
