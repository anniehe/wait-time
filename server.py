"""Flask server for NomNow!"""

from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import WaitTime, connect_to_db, db
from process_results import add_open_status, add_wait_info, sorted_result, filtered_result

from yelp_api import yelp
from google_api import BROWSER_KEY
from twilio_api import send_thank_you_sms, send_reminder_sms, convert_to_e164

import threading


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

    # Yelp API call with user input values
    search_results = yelp.search_query(term=search_term,
                                       location=location_term,
                                       category_filter="food,restaurants",
                                       limit=10)

    # result is the list of restaurant dictionaries
    result = search_results['businesses']

    # For each restaurant, add its open status and wait time info to their dictionary
    for restaurant in result:
        add_open_status(restaurant)
        add_wait_info(restaurant)

    # Handle sorting
    sort_value = request.args.get("sort_by")
    result = sorted_result(result, sort_value)

    # Handle filtering
    selected_filters = request.args.getlist("filter_by")
    result = filtered_result(result, selected_filters)

    # Add result to result_dict, which will be converted to a JSON through Jinja
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
    """Adds wait time information into database for a restaurant."""

    restaurant_name = request.form.get("restaurant_name")
    location = request.form.get("location")

    # Yelp API call to get the corresponding yelp id for the restaurant
    search_results = yelp.search_query(term=restaurant_name,
                                       location=location,
                                       category_filter="food,restaurants",
                                       limit=10)

    # restaurant_info is a dictionary of the restaurant's info
    restaurant_info = search_results['businesses'][0]

    yelp_id = str(restaurant_info['id'])
    quoted_hr = int(request.form.get("quoted_hr"))
    quoted_min = int(request.form.get("quoted_min"))

    # Convert quoted wait time into one value (quoted_minutes) for the database
    if quoted_hr != 0:
        quoted_minutes = quoted_min + (quoted_hr * 60)
    else:
        quoted_minutes = quoted_min

    # Interval for sms timer
    quoted_seconds = quoted_minutes * 60

    # Covert quoted wait time into string value for customized sms
    if quoted_hr and not quoted_min:
        quoted_time = "%d hr" % (quoted_hr)
    elif quoted_hr and quoted_min:
        quoted_time = "%d hr %d min" % (quoted_hr, quoted_min)
    elif quoted_min and not quoted_hr:
        quoted_time = "%d min" % (quoted_min)

    if request.form.get("phone_number"):
        raw_phone_number = str(request.form.get("phone_number"))
        phone_number = convert_to_e164(raw_phone_number)
        # Send thank you sms immediately
        send_thank_you_sms(phone_number, restaurant_name, quoted_time)
        # Send reminder sms after quoted time is up
        send_sms_timer = threading.Timer(
            quoted_seconds,
            send_reminder_sms,
            args=[phone_number, quoted_time, restaurant_name]
        )
        send_sms_timer.start()
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

    reported_wait_info = WaitTime(yelp_id=yelp_id,
                                  party_size=party_size,
                                  parties_ahead=parties_ahead,
                                  quoted_minutes=quoted_minutes,
                                  phone_number=phone_number)

    db.session.add(reported_wait_info)
    db.session.commit()

    flash("Thanks for reporting your wait time!")

    return redirect("/")


if __name__ == "__main__":
    app.debug = False

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
