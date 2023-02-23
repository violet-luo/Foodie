from flask import Flask, request, Response
import requests
import os
from dotenv import load_dotenv
import pymongo
import json

app = Flask(__name__)

### CONSTANTS ###
YELP_API_HOST = 'https://api.yelp.com'
BUSINESS_SEARCH_PATH = '/v3/businesses/search'

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

AUTHORIZATION_HEADERS = {
    'Authorization': 'Bearer {}'.format(os.environ.get('YELP_API_KEY'))
}

### HELPER FUNCTIONS ###

def convert_distance(distance, to_miles):
    """ Helper function to convert meters to miles and vice versa """
    return float(distance) / 1609.34 if to_miles else float(distance) / 0.000621371

def format_restaurants(response_json, exclude_id=None):
    """ Helper function that formats the response returned from the Yelp API to contain only relevant information """
    result = {
        "restaurants": []
    }
    for restaurant in response_json['businesses']:
        if exclude_id and restaurant["id"] == exclude_id:
            continue
        cleaned_data = {
            "yelp_id": restaurant["id"],
            "name": restaurant["name"],
            "rating": restaurant["rating"],
            "address": ' '.join(restaurant["location"]["display_address"]),
            "phone": restaurant["display_phone"],
            "distance": "{:0.2f}".format(convert_distance(restaurant["distance"], to_miles=True)),
            "price": restaurant["price"] if "price" in restaurant.keys() else "Not Available",
            "yelp_url": restaurant["url"]
        }
        result["restaurants"].append(cleaned_data)
    result["restaurants"].sort(key=lambda restaurant: float(restaurant["rating"]), reverse=True)
    return result

def mongoConnection():
    try:
        client = pymongo.MongoClient(os.environ.get('MONGO_DB_CLUSTER'))
        print('Successfully connected to Mongo DB!')
        db = client["restaurant_db"]
        col = db["favorites"]
        return col
    except:
        return Exception("Failed to connect to mongo db")

### API ENDPOINTS ###

@app.route('/reservations', methods=['GET'])
def find_reservations():
    """ Retrieves reservations available following the parameters (location, max_distance, reservation_time, 
    reservation_date, num_people) which are passed in as JSON in the request"""
    try:
        full_url = YELP_API_HOST + BUSINESS_SEARCH_PATH
        url_params = {
            "location": request.json['location'],
            "reservation_time": request.json['reservation_time'],
            "reservation_date": request.json['reservation_date'],
            "reservation_covers": request.json['num_people'],
            "radius": str(int(convert_distance(request.json['max_distance'], to_miles=False)))
        }
        response = requests.get(full_url, headers=AUTHORIZATION_HEADERS,params=url_params)
        return format_restaurants(response.json())
    except:
        return Response("Error retrieving restaurants from Yelp", status=400)

@app.route('/favorites', methods=['GET'])
def get_favorites():
    """ Fetches all saved restaurants from Mongo DB """
    try:
        col = mongoConnection()
    except:
        return Response(status=400)
    saved_favorites = col.find().sort("rating")
    restaurants = {
        "favorites": []
    }
    for record in saved_favorites:
        restaurants["favorites"].append(record)
    return Response(json.dumps(restaurants), status=200, mimetype="application/json")

@app.route('/favorite/<restaurant_yelp_id>', methods=['GET', 'POST', 'DELETE'])
def save_favorite_restaurant(restaurant_yelp_id):
    """ Saves restaurants information onto Mongo DB """
    try:
        col = mongoConnection()
    except:
        return Response(status=400)
    if request.method == 'POST':
        full_url = '{}/v3/businesses/{}'.format(YELP_API_HOST, restaurant_yelp_id)
        response = requests.get(full_url, headers=AUTHORIZATION_HEADERS)
        restaurant_data = response.json()
        new_restaurant_record = {
            "_id": restaurant_data["id"],
            "name": restaurant_data["name"],
            "rating": restaurant_data["rating"],
            "address": ' '.join(restaurant_data["location"]["display_address"]),
            "phone": restaurant_data["display_phone"],
            "price": restaurant_data["price"] if "price" in restaurant_data.keys() else "Not Available",
            "yelp_url": restaurant_data["url"]
        }
        col.insert_one(new_restaurant_record)
        response_body = {
            "restaurant_data": new_restaurant_record,
            "message": "favorite restaurant saved successfully!"
        }
        return Response(json.dumps(response_body), status=201, mimetype="application/json")
    elif request.method == 'DELETE':
        document = col.find_one({"_id": restaurant_yelp_id})
        if not document:
            return Response(json.dumps({"message": "No restaurant with given id found"}), status=404, mimetype="application/json")
        col.delete_one({"_id": restaurant_yelp_id})
        response_body = {
            "deleted_id": restaurant_yelp_id,
            "message": "Successfully removed restaurant from favorites"
        }
        return Response(json.dumps(response_body), status=200, mimetype="application/json")
    else:
        document = col.find_one({"_id": restaurant_yelp_id})
        if not document:
            return Response(json.dumps({"message": "No restaurant with given id found"}), status=404, mimetype="application/json")
        response_body = {
            "restaurant_data": document,
            "message": "Successfully retrieved restaurant from favorites"
        }
        return Response(json.dumps(response_body), status=200, mimetype="application/json")

@app.route("/recommendations", methods=['GET'])
def get_recommendations():
    """ Gets similar restaurants in a given location (JSON parameters passed in: yelp_restaurant_id, location, max_distance) """
    try:
        restaurant_url = '{}/v3/businesses/{}'.format(YELP_API_HOST, request.json['yelp_restaurant_id'])
        restaurant_response = requests.get(restaurant_url, headers=AUTHORIZATION_HEADERS)
        restaurant_data = restaurant_response.json()
        category_list = [category["alias"] for category in restaurant_data["categories"]]
        restaurant_categories = ','.join(category_list)
        url_params = {
            "categories": restaurant_categories,
            "location": request.json["location"],
            "radius": str(int(convert_distance(request.json['max_distance'], to_miles=False)))
        }
        full_url = YELP_API_HOST + BUSINESS_SEARCH_PATH
        recommended_response = requests.get(full_url, headers=AUTHORIZATION_HEADERS,params=url_params)
        formatted_restaurants = format_restaurants(recommended_response.json(), exclude_id=request.json['yelp_restaurant_id'])
        return Response(json.dumps(formatted_restaurants), status=200)
    except:
        return Response(status=400)

if __name__ == "__main__":
    app.run(host='0.0.0.0')