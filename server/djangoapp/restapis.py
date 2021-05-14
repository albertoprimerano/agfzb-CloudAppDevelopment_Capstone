import requests
import json

from django.http import HttpResponse

from .models import CarDealer, CarReview
from requests.auth import HTTPBasicAuth


# Handle all get requests
def get_request(url, **kwargs):
    print("GET from {} ".format(url))
    if "api_key" in kwargs.keys():
        api_key = kwargs["api_key"]
    else:
        api_key = False
    try:
        if api_key:
            params = dict()
            params["version"] = kwargs["version"]
            params["text"] = kwargs["text"]
            params["features"] = kwargs["features"]
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=params,
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Handle post requests
def post_request(url, json_payload, **kwargs):
    print("POST from {} ".format(url))
    try:
          response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Returns the list of dealers for a given state
def get_dealers_by_state(url, dealer_state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=dealer_state)
    try:
        if json_result:
            # Get the row list in JSON as dealers
            dealers = json_result["entries"]
            # For each dealer object
            for dealer_doc in dealers:
                # Get its content in `doc` object
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                       full_name=dealer_doc["full_name"],
                                       id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                       short_name=dealer_doc["short_name"],
                                       st=dealer_doc["st"], zip=dealer_doc["zip"])
                results.append(dealer_obj)
    except:
        print("Error occurred retrieving dealers by state: {state}".format(state=dealer_state))
    return results


# Retrieve the dealer details and return the first result
def get_dealers_by_id(url, dealer_id):
    result = []
    # Call get_request with a URL parameter
    try:
        json_result = get_request(url, dealer_id=dealer_id)
        if json_result:
            dealer_doc = json_result["entries"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            result = dealer_obj
    except:
        print("Error occurred retrieving dealers by id: {id}".format(id=dealer_id))
    return result


# Retrieve a list of dealers from Cloudant and return in a list of CarDealer objects
def get_dealers_from_cf(url, **kwargs):
    results = []
    try:
        # Call get_request with a URL parameter
        json_result = get_request(url)
        if json_result:
            # Get the row list in JSON as dealers
            dealers = json_result["entries"]
            # For each dealer object
            for dealer_doc in dealers:
                # Get its content in `doc` object
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                       full_name=dealer_doc["full_name"],
                                       id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                       short_name=dealer_doc["short_name"],
                                       st=dealer_doc["st"], zip=dealer_doc["zip"])
                results.append(dealer_obj)
    except:
        print("Error occurred retrieving dealers")
    return results


# Get reviews for a specific dealer_id
def get_dealer_review_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    try:
        json_result = get_request(url, dealerId=dealer_id)
        if json_result:
            if '404' in json_result.keys():
                return ""
            # Get the row list in JSON as dealers
            reviews = json_result["entries"]
            # For each review object
            for review_doc in reviews:
                # Create a DealerReview object with values in `doc` object
                if bool(review_doc):
                    purchase_date = ""
                    car_make = ""
                    car_model = ""
                    car_year = ""
                    # if purchased some field are populated
                    if review_doc["purchase"]:
                        purchase_date = review_doc["purchase_date"]
                        car_make = review_doc["car_make"]
                        car_model = review_doc["car_model"]
                        car_year = review_doc["car_year"]
                    dealer_review_obj = CarReview(dealership=review_doc["dealership"], name=review_doc["name"],
                                                  purchase=review_doc["purchase"], id=review_doc["id"],
                                                  review=review_doc["review"], purchase_date=purchase_date,
                                                  car_make=car_make, car_model=car_model,
                                                  car_year=car_year, sentiment="neutral")
                    # add sentiment analysis
                    print(dealer_review_obj.review)
                    try:
                        dealer_review_obj.sentiment=analyze_review_sentiments(dealer_review_obj.review)
                    except:
                        print("Error on retrieving sentiment")
                    results.append(dealer_review_obj)
    except:
        print("Error occurred retrieving reviews for dealer with id: {id}".format(id=dealer_id))
    return results


# Analyze sentiments for a given text
def analyze_review_sentiments(text):
    api_key = "2nJ7aKyXewvSh-M_8_YtNxf9hjnkyQH4ZBJQiVByJheh"
    ibm_nlu_url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/"
    ibm_nlu_instance = "28b7c08d-741f-448a-a3ed-fc0da2435807/v1/analyze"
    url = ibm_nlu_url + ibm_nlu_instance
    # request to the specific url
    response = get_request(url,
                           text=text, version="2020-08-01",
                           api_key=api_key, features="sentiment")
    return response["sentiment"]["document"]["label"]



