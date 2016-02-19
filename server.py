from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import WaitTime, connect_to_db, db

from yelpapi import YelpAPI
from google_api import get_place_id, get_opening_hours_info
import os

from datetime import datetime
import humanize


### GOOGLE MAPS API ###
BROWSER_KEY = os.environ['GOOGLE_BROWSER_KEY']


### YELP API ###
CONSUMER_KEY = os.environ['YELP_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['YELP_CONSUMER_SECRET']
TOKEN = os.environ['YELP_TOKEN']
TOKEN_SECRET = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET)


### FLASK APP ###
app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "SHHHHH"

# Raises an error an undefined variable in Jinja2 is used
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

    # before_yelp = datetime.now()
    # Yelp API call from user input values
    search_results = yelp_api.search_query(term=search_term,
                                           location=location_term,
                                           category_filter="food,restaurants")
    # after_yelp = datetime.now()
    # print after_yelp - before_yelp, "YELP"

    # result is the list of business dictionaries
    result = search_results['businesses']

    # Add opening hours/open now info from Google Places and wait time info from
    # database to each business dictionary
    for business in result:

        # before_google = datetime.now()
        add_restaurant_open_info(business)
        # after_google = datetime.now()
        # print after_google - before_google, "GOOGLE"

        # before_wait = datetime.now()
        add_wait_info(business)
        # after_wait = datetime.now()
        # print after_wait - before_wait, "WAIT"

    # Sort by shortest wait time if checkbox is checked
    if request.args.get("sort_by") == "wait_time":
        result.sort(key=lambda business: business['quoted_wait_time'])

    # Add result to result_dict, which will be converted to a JSON through Jinja.
    result_dict = {'result': result}

    return render_template("results.html",
                           result=result,
                           key=BROWSER_KEY,
                           result_dict=result_dict,
                           search_term=search_term,
                           location_term=location_term)


@app.route("/find_restaurant")
def display_restaurant_search_form():
    """Display restaurant search form to select for restaurant to report wait time."""

    return render_template("find_restaurant.html",
                           key=BROWSER_KEY)


# @app.route("/search_yelp")
# def find_restaurant():
#     """Searches Yelp API for restaurant(s) that matches user search."""

#     search_term = request.args.get("restaurant")
#     location_term = request.args.get("location")

#     # Yelp API call from user input values
#     search_results = yelp_api.search_query(term=search_term,
#                                            location=location_term,
#                                            category_filter="food,restaurants",
#                                            limit=3)

#     # result is the list of business dictionaries
#     result = search_results['businesses']

#     for business in result:
#         name = business['name'].lower
#         address = business['location']['address'][0]
#         city = business['location']['city']

#     return render_template("wait_time_form.html",
#                            name=name,
#                            address=address,
#                            city=city,
#                            state_code=state_code,
#                            )


@app.route("/report")
def display_wait_time_form():
    """Display form to report wait time."""

    return render_template("wait_time_form.html",
                           key=BROWSER_KEY)


@app.route("/process_report", methods=["POST"])
def process_wait_time_form():
    """Adds wait time information into database if for valid restaurant."""

    # restaurant_name = request.form.get("restaurant_name")
    # location = request.form.get("location")

    # search_results = yelp_api.search_query(term=search_term,
    #                                        location=location_term,
    #                                        category_filter="food,restaurants")

    # # result is the list of business dictionaries
    # result = search_results['businesses']

    wait_test = WaitTime(yelp_id="sanraku-san-francisco-2",
                         party_size=4,
                         quoted_minutes=150,
                         parties_ahead=8)

    db.session.add(wait_test)
    db.session.commit()

    return redirect("/")


### HELPER FUNCTIONS ###

def add_restaurant_open_info(business):
    """Add opening hours and open now information to the business dictionary."""

    # Find matching Google Places info for the Yelp result
    name = business['name']
    address = business['location']['address'][0]
    city = business['location']['city']
    location_lat = business['location']['coordinate']['latitude']
    location_lng = business['location']['coordinate']['longitude']

    keyword = "%s %s %s" % (name, address, city)
    location = "%f,%f" % (location_lat, location_lng)

    # Get place_id from Google Places API for the Yelp result
    # to check for opening hours and open now info
    place_id = get_place_id(keyword, location)

    if not place_id:
        opening_hours_info = None
        open_now = "Open now unknown"
    else:
        restaurant_hours_info = get_opening_hours_info(place_id)
        if restaurant_hours_info:
            opening_hours_info, open_now = restaurant_hours_info
            if open_now is True:
                open_now = "Open now"
            elif open_now is False:
                open_now = "Closed"
        else:
            opening_hours_info = None
            open_now = "Open now unknown"

    # Add opening hours and open now info to dictionary
    business['opening_hours'] = opening_hours_info
    business['open_now'] = open_now


def add_wait_info(business):
    """Add wait time information from database to the business dictionary."""

    yelp_id = business['id']

    # Find the most recent wait time info for a restaurant from the database.
    # For records with the same timestamp, fetch the largest quoted wait time.
    wait_info = (WaitTime.query.filter_by(yelp_id=yelp_id)
                 .order_by(WaitTime.timestamp.desc(), WaitTime.quoted_minutes.desc())
                 .first()
                 )

    # Add wait time info to business dictionary
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


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
