from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import WaitTime, connect_to_db, db

from yelpapi import YelpAPI
from google_api import get_place_id, get_opening_hours_info
import os

from datetime import datetime, timedelta
import humanize

import phonenumbers

from celery import Celery

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


### Celery ###

# Celery is an asynchronous task queue with real-time processing and task scheduling.
# A Celery client is created and will run with the Flask app.
# Celery communicates with Celery workers through Redis, the message broker.
# Celery workers will fetch the task from the message queue and execute the task.

celery = Celery(app)
celery.config_from_object('celeryconfig')


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

    before_yelp = datetime.now()
    # Yelp API call from user input values
    search_results = yelp_api.search_query(term=search_term,
                                           location=location_term,
                                           category_filter="food,restaurants",
                                           limit=10)
    after_yelp = datetime.now()
    print after_yelp - before_yelp, "YELP"

    # result is the list of business dictionaries
    result = search_results['businesses']

    # Add opening hours/open now info from Google Places and wait time info from
    # database to each business dictionary
    for business in result:

        before_google = datetime.now()
        add_restaurant_open_info(business)
        after_google = datetime.now()
        print after_google - before_google, "GOOGLE"

        before_wait = datetime.now()
        add_wait_info(business)
        after_wait = datetime.now()
        print after_wait - before_wait, "WAIT"

    after_loop = datetime.now()
    print after_loop - before_yelp, "TOTAL TIME"

    # Handle sorting
    sort_value = request.args.get("sort_by")
    result = sorted_result(result, sort_value)

    # Handle filtering
    selected_filters = request.args.getlist("filter_by")
    result = filtered_result(result, selected_filters)

    # Add result to result_dict, which will be converted to a JSON through Jinja.
    result_dict = {'result': result}

    return render_template("results.html",
                           result=result,
                           key=BROWSER_KEY,
                           result_dict=result_dict,
                           search_term=search_term,
                           location_term=location_term)


@app.route("/report")
def display_wait_time_form():
    """Display form to report wait time."""

    return render_template("wait_time_form.html",
                           key=BROWSER_KEY)


@app.route("/process_report", methods=["POST"])
def process_wait_time_form():
    """Adds wait time information into database if for valid restaurant."""

    restaurant_name = request.form.get("restaurant_name")
    location = request.form.get("location")

    # Yelp API call with restaurant name and location values
    # parsed from selected restaurant using autocomplete
    # to get the corresponding yelp id
    search_results = yelp_api.search_query(term=restaurant_name,
                                           location=location,
                                           category_filter="food,restaurants",
                                           limit=1)

    # restaurant_info is a dictionary
    restaurant_info = search_results['businesses'][0]

    yelp_id = str(restaurant_info['id'])
    quoted_hr = int(request.form.get("quoted_hr"))
    quoted_min = int(request.form.get("quoted_min"))

    # Convert quoted wait time into one value
    if quoted_hr != 0:
        quoted_minutes = quoted_min + (quoted_hr * 60)
    else:
        quoted_minutes = quoted_min

    if request.form.get("phone_number"):
        raw_phone_number = str(request.form.get("phone_number"))
        phone_number = convert_to_e164(raw_phone_number)
    else:
        phone_number = None

    if request.form.get("party_size"):
        party_size = int(request.form.get("party_size"))
    else:
        party_size = None

    if request.form.get("parties_ahead"):
        parties_ahead = int(request.form.get("parties_ahead"))
    else:
        parties_ahead = None

    timestamp = datetime.utcnow()
    timediff = timedelta(minutes=quoted_minutes)
    estimated_time = timestamp + timediff

    reported_wait_info = WaitTime(yelp_id=yelp_id,
                                  party_size=party_size,
                                  quoted_minutes=quoted_minutes,
                                  parties_ahead=parties_ahead,
                                  estimated_time=estimated_time,
                                  phone_number=phone_number)

    db.session.add(reported_wait_info)
    db.session.commit()

    flash("Thanks for reporting your wait time!")

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

            # opening_hours_info is a list of day:hoursopen-hoursclose
            # loop over the list
                # for item in string, slice and grab everything up until the colon
                    # grab today's day using datetime
                    # compare the two, if it is that day
                # take that element and add to dictinoary for the current day

            # day_of_week = datetime.now().date().weekday()

            # if day_of_week == 0:
            #     day_of_week = "Monday"
            # elif day_of_week == 1:
            #     day_of_week = "Tuesday"
            # elif day_of_week == 2:
            #     day_of_week = "Wednesday"
            # elif day_of_week == 3:
            #     day_of_week = "Thursday"
            # elif day_of_week == 4:
            #     day_of_week = "Friday"
            # elif day_of_week == 5:
            #     day_of_week = "Saturday"
            # elif day_of_week == 5:
            #     day_of_week = "Sunday"

            # for item in opening_hours_info:
            #     day_hours_info = item.split(":")
            #     day = day_hours_info[0]
            #     if day == day_of_week:
            #         day_hours = item
            #         break
            # business['todays_hours'] = day_hours

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
        # business['timestamp'] = humanize.naturaltime(datetime.utcnow() - wait_info.timestamp)
        business['timestamp'] = wait_info.timestamp
        business['timestamp_value'] = wait_info.timestamp

        if wait_info.party_size:
            business['party_size'] = wait_info.party_size
        else:
            business['party_size'] = "N/A"

        if wait_info.parties_ahead:
            business['parties_ahead'] = wait_info.parties_ahead
        else:
            business['parties_ahead'] = "N/A"

    else:
        business['quoted_wait_time'] = "Not available"
        business['party_size'] = "N/A"
        business['parties_ahead'] = "N/A"
        business['timestamp'] = datetime(2222, 2, 2)
        # business['timestamp'] = "N/A"
        business['timestamp_value'] = datetime(2222, 2, 2)


def sorted_result(result, sort_value):
    """Returns result sorted by the selected value."""

    # Sort by shortest wait time
    if sort_value == "wait_time":
        result.sort(key=lambda business: business['quoted_wait_time'])

    # Sort by recently reported
    if sort_value == "recent_report":
        result.sort(key=lambda business: business['timestamp_value'])

    # Sort by highest rating
    if sort_value == "rating":
        result.sort(key=lambda business: business['rating'], reverse=True)

    # Sort by most reviews
    if sort_value == "review_count":
        result.sort(key=lambda business: business['review_count'], reverse=True)

    return result


def filtered_result(result, selected_filters):
    """Returns filtered result."""

    # Filter by open now
    if "open_now" in selected_filters:
        new_result = []
        for business in result:
            if business['open_now'] == "Open now":
                new_result.append(business)
        result = new_result

    # Filter by <=15 min wait
    if "15_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if business['quoted_wait_time'] != "Not available" and business['quoted_wait_time'] <= 15:
                new_result.append(business)
        result = new_result

    # Filter by <=30 min wait
    if "30_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if business['quoted_wait_time'] != "Not available" and business['quoted_wait_time'] <= 30:
                new_result.append(business)
        result = new_result

    # Filter by <=45 min wait
    if "45_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if business['quoted_wait_time'] != "Not available" and business['quoted_wait_time'] <= 45:
                new_result.append(business)
        result = new_result

    # Filter by <=60 min wait
    if "60_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if business['quoted_wait_time'] != "Not available" and business['quoted_wait_time'] <= 60:
                new_result.append(business)
        result = new_result

    return result


def convert_to_e164(raw_phone):
    """Formats phone numbers to E.164 format for Twilio.

        >>> convert_to_e164("4235432224")
        u'+14235432224'

        >>> convert_to_e164("(423)543-2224")
        u'+14235432224'

        >>> convert_to_e164("423.543.2224")
        u'+14235432224'

    """

    if not raw_phone:
        return

    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # If no country code information present, assume it's a US number
        parse_type = "US"

    phone_representation = phonenumbers.parse(raw_phone, parse_type)

    return phonenumbers.format_number(phone_representation,
                                      phonenumbers.PhoneNumberFormat.E164)


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
