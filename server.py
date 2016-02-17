from flask import Flask, render_template, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import WaitTime, connect_to_db, db

from yelpapi import YelpAPI
from google_api import get_place_id, get_opening_hours_info
import os

from datetime import datetime
import humanize


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "SHHHHH"

# This raises an error if you use an undefined variable in Jinja2.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


@app.route("/search")
def display_search_results():
    """Display search results."""

    search_term = request.args.get("keyword")

    location_term = request.args.get("location")
    if not location_term:
        location_term = "San Francisco"

    search_results = yelp_api.search_query(term=search_term,
                                           location=location_term,
                                           category_filter="food,restaurants")

    # result is the list of businesses
    result = search_results['businesses']

    # Each business is a dictionary
    for business in result:

        name = business['name']
        address = business['location']['address'][0]
        city = business['location']['city']
        location_lat = business['location']['coordinate']['latitude']
        location_lng = business['location']['coordinate']['longitude']

        keyword = "%s %s %s" % (name, address, city)
        location = "%f,%f" % (location_lat, location_lng)

        # Get place_id from Google API for the business result from Yelp
        place_id = get_place_id(keyword, location)

        # If there's a match, add opening_hours_info and open_now to the dictionary
        if not place_id:
            opening_hours_info = None
            open_now = "Open now unknown"
        else:
            # If there are opening hours info for the place id
            if get_opening_hours_info(place_id):
                opening_hours_info, open_now = get_opening_hours_info(place_id)
                if open_now is True:
                    open_now = "Open now"
                elif open_now is False:
                    open_now = "Closed"
            else:
                opening_hours_info = None
                open_now = "Open now unknown"

        business['opening_hours'] = opening_hours_info
        business['open_now'] = open_now

        yelp_id = business['id']

        # The most recent wait time info for a restaurant
        # If same timestamp, fetch the largest quoted wait time
        wait_info = (WaitTime.query.filter_by(yelp_id=yelp_id)
                     .order_by(WaitTime.timestamp.desc(), WaitTime.quoted_minutes.desc())
                     .first()
                     )

        # If there is wait time info for a restaurant, add to dictionary
        if wait_info:
            business['quoted_wait_time'] = wait_info.quoted_minutes
            business['party_size'] = wait_info.party_size
            business['parties_ahead'] = wait_info.parties_ahead
            business['timestamp'] = humanize.naturaltime(datetime.utcnow() - wait_info.timestamp)
        else:
            business['quoted_wait_time'] = "Not available"
            business['party_size'] = "Not available"
            business['parties_ahead'] = "Not available"
            business['timestamp'] = "Not available"

    # ADD SORT FEATURE IN FORM: sort by quoted_wait_time (shortest first)
    # if request.args.get('sort') == quoted_wait_time, then run code below
    # result.sort(key=lambda business: business['quoted_wait_time'])

    # result is now a list of businesses with wait time info and hours info added
    result_dict = {'result': result}

    return render_template("results.html",
                            result=result,
                            key=browser_key,
                            result_dict=result_dict)


# @app.route("/results.json")
# def get_results_info():
#     """Return search results info as JSON."""

#     # NOT GETTING SEARCH TERM AND LOCATION TERM FROM FORM.

#     search_term = request.args.get("keyword")

#     location_term = request.args.get("location")
#     if not location_term:
#         location_term = "San Francisco"

#     search_results = yelp_api.search_query(term=search_term,
#                                            location=location_term,
#                                            category_filter="food,restaurants")

#     # result is a list of dictionaries of businesses
#     result = search_results['businesses']
#     results_dict = {}

#     # Each business is a dictionary of business info
#     for business in result:
#         yelp_id = business['id']
#         name = business['name']
#         location_lat = business['location']['coordinate']['latitude']
#         location_lng = business['location']['coordinate']['longitude']

#         results_dict[yelp_id] = {'name': name,
#                                  'location_lat': location_lat,
#                                  'location_lng': location_lng}

#     return jsonify(results_dict)


### GOOGLE API ###
browser_key = os.environ['GOOGLE_BROWSER_KEY']


### YELP API ###

consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
