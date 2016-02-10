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
                                           category_filter='food,restaurants',
                                           limit=4)

    # result is the list of businesses
    result = search_results['businesses']

    # Each item is a dictionary of business info in result (list of businesses)
    for item in result:

        name = item['name']
        location_lat = str(item['location']['coordinate']['latitude'])
        location_lng = str(item['location']['coordinate']['longitude'])
        address = item['location']['address'][0]
        city = item['location']['city']

        keyword = name + " " + address + " " + city
        location = location_lat + "," + location_lng

        # print "KEYWORD", keyword
        # print "LOCATION", location

        # Get place_id for the business result from Yelp
        place_id = get_place_id(keyword, location)

        # If there's a match, add opening_hours_info and open_now to the dictionary
        if not place_id:
            opening_hours_info = "not available"
            open_now = "Open now unknown"
        else:
            ##### Take off limit and ERROR right here after refactoring google_api code #####
            opening_hours_info, open_now = get_opening_hours_info(place_id)
            if not opening_hours_info:
                opening_hours_info = "not available"

            if open_now is None:
                open_now = "Open unknown"
            elif open_now is True:
                open_now = "Open now"
            elif open_now is False:
                open_now = "Closed"

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
