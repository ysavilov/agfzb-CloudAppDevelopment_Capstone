import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests

# 
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        #  if api_key:
             # Basic authentication GET
             # request.get(url, params=params, auth=, ...)
             # else:
             # # no authentication GET
             # request.get(url, params=params)
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# this make post request to flask server: reviews.py
def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("An error occurred while making POST request. ")
    status_code = response.status_code
    print(f"With status {status_code}")

    return response


    

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        print("JSON RESULT: ", json_result)
        # Get the row list in JSON as dealers
        # dealers = json_result[0]
        #
        # First Run Node.js Server on 3000 Port 
        # Second Run Pyserver on 8000 Port then
        # copy the nodes server url running on port 3000 and place it in views file get_dealership
        #
        #json_result = [{}, {}, {}...] So iterte over each document.
        #
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer
            print("DEALER DOC", dealer_doc)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealer_id):
# - Call get_request() with specified arguments
    results = [{}]
    
    url_with_id = "{url}?id={dealer_id}".format(url=url, dealer_id=dealer_id)
    json_result = get_request(url_with_id)
    # - Parse JSON results into a DealerView object list
    dealers = json_result
    # For each dealer in the response
    for dealer in dealers:
        print(dealer)
        dealer_doc = dealer
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
        results.append(dealer_obj)

    return results



# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        reviews = json_result
        # print("Revs________________")
        # print(reviews)
        # print("________________")
        
        for single_review in reviews:
            # ... (print statements)
            # print("SRevs________________")
            # print(single_review)
            # print("________________")
            
            # Creating a review object
            # Use .get() Method: Use .get(key, default_value) to access dictionary values gracefully, avoiding KeyError without the need for a try...except block.
            dealer_review = DealerReview(  # Create object initially
                id=single_review["id"],
                name=single_review["name"],
                dealership=single_review["dealership"],
                review=single_review["review"],
                purchase=single_review.get("purchase"),
                purchase_date=single_review.get("purchase_date"),
                car_make=single_review.get("car_make"),
                car_model=single_review.get("car_model"),
                car_year=single_review.get("car_year"),
                sentiment="",
            )

            # Analysing the sentiment of the review object's review text and saving it to the object attribute "sentiment"
            dealer_review.sentiment = analyze_review_sentiments(dealer_review.review)

            # Saving the review object to the list of results
            results.append(dealer_review)
            print("DEALER REVIEW:", dealer_review)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# Natural Language Understanding-09
service_creditentials = {"apikey": "e_lCizYSt2HdrPg0t_nVwCbNGF5z7H-c0NF1iGZ9KfH2","url": "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/81a757e0-3a32-4885-a895-52697bcd1da4"}

def analyze_review_sentiments(dealerreview):
    body = {"text": dealerreview, "features": {"sentiment": {"document": True}}}
    print(dealerreview)
    response = requests.post(
        service_creditentials["url"] + "/v1/analyze?version=2019-07-12", # watson_url
        headers={"Content-Type": "application/json"},
        json=body,  # Use json parameter for automatic conversion
        auth=HTTPBasicAuth("apikey", service_creditentials["apikey"]), # watson_api_key
    )

    # Check if request was successful
    if response.status_code == 200:
        sentiment = response.json()["sentiment"]["document"]["label"]
        return sentiment
    return "N/A"
