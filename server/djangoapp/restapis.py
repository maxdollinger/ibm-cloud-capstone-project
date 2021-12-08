import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


REVIEW_URL = "https://2e35c4b8.eu-gb.apigw.appdomain.cloud/api/review"
DEALERSHIP_URL = "https://2e35c4b8.eu-gb.apigw.appdomain.cloud/api/dealership"
# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Network exception occurred")
    

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Network exception occured")
    


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(**kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(DEALERSHIP_URL)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(dealer_doc)
            results.append(dealer_obj)

    return results

def get_dealers_by_state(state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(DEALERSHIP_URL, state=state)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(dealer_doc)
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(dealer_id):
    json_result = get_request(DEALERSHIP_URL, id=dealer_id)
    if json_result:
        return json_result["body"]
    else:
        return {'message': 'Something went wrong'}

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(REVIEW_URL, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["body"]
        # For each dealer object
        for review in reviews:
            sentiment = analyze_review_sentiments(review['review'])
            review_obj = DealerReview(review, sentiment)
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    url = os.environ.get('NLU_API_URL') 
    api_key = os.environ.get('NLU_API_KEY')

    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-12-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    try:
        response = natural_language_understanding.analyze( text=dealerreview,features=Features(sentiment=SentimentOptions(targets=[dealerreview]))).get_result()
    except:
        response = {'sentiment': {'document': {'label': 'neutral'}}}

    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 

    return(label) 



