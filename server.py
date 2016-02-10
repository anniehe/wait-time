from flask import Flask, render_template, request
from yelpapi import YelpAPI
from google_api import *
import os

app = Flask(__name__)


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


@app.route("/search")
def display_search_results():
    """Display search results."""

    search_term = request.args.get('keyword')

    location_term = request.args.get('location')
    if not location_term:
        location_term = 'San Francisco'

    search_results = yelp_api.search_query(term=search_term,
                                           location=location_term,
                                           category_filter='food,restaurants')

    # result is the list of businesses
    result = search_results['businesses']

    # Each item is a dictionary of business info in result (list of businesses)
    for item in result:

        name = item['name']
        address = item['location']['address'][0]
        city = item['location']['city']
        location_lat = item['location']['coordinate']['latitude']
        location_lng = item['location']['coordinate']['longitude']

        keyword = "%s %s %s" % (name, address, city)
        location = "%f,%f" % (location_lat, location_lng)

        # print "KEYWORD", keyword
        # print "LOCATION", location

        # Get place_id from Google API for the business result from Yelp
        place_id = get_place_id(keyword, location)

        # print "PLACE ID", place_id

        # If there's a match, add opening_hours_info and open_now to the dictionary
        if not place_id:
            opening_hours_info = None
            open_now = "Open now unknown"
        else:
            # print "GET OPENING HOURS FROM PLACE ID", get_opening_hours_info(place_id)

            # If there are opening hours information for the place id
            if get_opening_hours_info(place_id):
                opening_hours_info, open_now = get_opening_hours_info(place_id)
                if open_now is True:
                    open_now = "Open now"
                elif open_now is False:
                    open_now = "Closed"
            else:
                opening_hours_info = None
                open_now = "Open now unknown"

        item['opening_hours'] = opening_hours_info
        item['open_now'] = open_now

    return render_template("results.html", result=result)


### YELP API ###

consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)


if __name__ == "__main__":
    app.debug = True

    app.run()
