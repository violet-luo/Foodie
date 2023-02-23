# Team Name: Foodie

## 👥 Members
* Gabe Espinosa
* Jahoe Lee
* Violet Luo
* Zhizhong Wu
* Megan Yang

## 🌐 APIs used in the project

* Yelp API (https://docs.developer.yelp.com/docs/endpoints-4) allows us to perform searches on the restaurants that are listed on Yelp, where we can get specific information such as address, rating, open time, phone number, etc. It also allows us to make reservations on restaurants that are still available.
* Google Maps API (https://developers.google.com/maps/documentation/places/web-service) will respond with a map that shows the location of the restaurant we specified, or it can suggest what are the nearby restaurants.

## ✏️ Description
For the API we plan to build, the user will input a location, time, and maximum distance to search for specific reservations. Then, using the Yelp API, all restaurants with an available reservation in the area inputted by the user will be returned. The API will also allow users to save their favorite restaurants, which will persist on a database (MongoDB/MySQL), and allow them to search for their favorite restaurants and similar ones as well. The API will also allow us to retrieve the relevant information of restaurants that are close to a specific location, our backend will give the recommendation of restaurants based on their customer rating.
