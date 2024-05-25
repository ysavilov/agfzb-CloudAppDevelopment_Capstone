from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.urls import reverse
import logging
import json

from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request

from django.views.decorators.csrf import csrf_exempt, csrf_protect

from .models import CarModel, CarDealer

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/contact.html", context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # handle post request
    if request.method == "POST":
        # get use name and password from post request
        username = request.POST['username']
        password = request.POST['psw']

        # authenticate user
        user = authenticate(username=username, password=password)
        # if authorized log in and redirect else do not login
        if user is not None:
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return redirect("djangoapp/index.html")
    else:
        return redirect("djangoapp/index.html")


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
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
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
# make request to node.js server: get-dealerships.js
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        # https://devshahfahad-8000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp
        # url = "https://devshahfahad-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        url = "http://localhost:3000/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# make request to flask server: reviews.py
def get_dealer_details(request, dealer_id):
    print(request, dealer_id)
    if request.method == "GET":
        context = {}
        url = f"http://127.0.0.1:5000/api/get_reviews?id={dealer_id}"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url)
        # Concat all dealer's short name
        dealer_names = " ".join([dealer.name for dealer in reviews])
        # Return a list of dealer short name
        
        context = {"reviews" :reviews, "dealer_id": dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    # User must be logged in before posting a review
    if request.user.is_authenticated or True:
        # GET request renders the page with the form for filling out a review
        if request.method == "GET":
            # url = f"http://localhost:3000/dealerships/get?dealerId={dealer_id}"
            url = "http://localhost:3000/dealerships/get"
            # Get dealer details from the API
            # Get dealer details from the API
            dealer = get_dealer_by_id_from_cf(url, dealer_id=dealer_id) # return [{}, {dealer object}]
            # temprory solution is to extract dealer object at index 1: dealer[1]
            context = {
                "cars": CarModel.objects.all(),
                "dealer": dealer[1],
            }
            
            return render(request, 'djangoapp/add_review.html', context)
        
        # POST request posts the content in the review submission form to the Cloudant DB using the post_review Cloud Function
        if request.method == "POST":
            # Get data from request
            review_post_json_data = request.POST # Loads data only from form
            # review_post_json_data = json.loads(request.body) # Loads json data from post request
            print("AT POST REQUEST: ")
            print(request.POST)
            # Store data to review dictionary one by one
            review = {}
            review["id"] = review_post_json_data.get("id")
            review["name"] = review_post_json_data.get("name")
            review["dealership"] = dealer_id
            review["review"] = review_post_json_data.get("review")
            review["purchase"] = review_post_json_data.get("purchase", False)  # Default to False if not present

            if review["purchase"]:
                purchase_date_str = review_post_json_data.get("purchase_date")
                purchase_date_str = review_post_json_data.get("purchase_date")
                if purchase_date_str:
                    purchase_date = datetime.strptime(purchase_date_str, "%m/%d/%Y")
                    review["purchase_date"] = purchase_date.strftime("%m/%d/%Y")
                else:
                    review["purchase_date"] = None
            else:
                review["purchase_date"] = None

            print("AT Review:  ")
            print(review)
            car = get_object_or_404(CarModel, pk=review["id"])
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            
        #     # make reques to this url: flask server: reviews.py
            url = "http://127.0.0.1:5000/api/post_review"  # API Cloud Function route
            json_payload = {"review": review}  # Create a JSON payload that contains the review data
            
            # Performing a POST request with the review
            print("JSON PAYLOAD IS HERE: ", json_payload)
            # After posting the review the user is redirected back to the dealer details page
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            

    # If user isn't logged in, redirect to login page
    print("User must be authenticated before posting a review. Please log in.")
    return redirect("/djangoapp/login")
