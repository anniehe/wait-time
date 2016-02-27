from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

from model import WaitTime, connect_to_db, db

from yelp_api import yelp
from google_api import is_open_now, BROWSER_KEY
from twilio_api import send_thank_you_sms, send_reminder_sms, convert_to_e164

from datetime import datetime, timedelta
import arrow
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

    before_yelp = datetime.now()
    # Yelp API call from user input values
    search_results = yelp.search_query(term=search_term,
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
        add_open_status(business)
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
    search_results = yelp.search_query(term=restaurant_name,
                                       location=location,
                                       category_filter="food,restaurants",
                                       limit=1)

    # restaurant_info is a dictionary
    restaurant_info = search_results['businesses'][0]

    yelp_id = str(restaurant_info['id'])
    quoted_hr = int(request.form.get("quoted_hr"))
    quoted_min = int(request.form.get("quoted_min"))

    # Convert quoted wait time into one value for the database
    if quoted_hr != 0:
        quoted_minutes = quoted_min + (quoted_hr * 60)
    else:
        quoted_minutes = quoted_min

    # Time logic for sms
    quoted_seconds = quoted_minutes * 60

    if quoted_hr and not quoted_min:
        quoted_time = str(quoted_hr) + " hr"
    elif quoted_hr and quoted_min:
        quoted_time = str(quoted_hr) + " hr " + str(quoted_min) + " min"
    elif quoted_min and not quoted_hr:
        quoted_time = str(quoted_min) + " min"

    if request.form.get("phone_number"):
        raw_phone_number = str(request.form.get("phone_number"))
        phone_number = convert_to_e164(raw_phone_number)
        # Send thank you sms
        send_thank_you_sms(phone_number, restaurant_name, quoted_time)
        # Send sms reminder after quoted time is up
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

def add_open_status(business):
    """Add open status at the current time to the business dictionary."""

    # Find matching Google Places info for the Yelp result
    name = business['name']
    address = business['location']['address'][0]
    city = business['location']['city']
    location_lat = business['location']['coordinate']['latitude']
    location_lng = business['location']['coordinate']['longitude']

    keyword = "%s %s %s" % (name, address, city)
    location = "%f,%f" % (location_lat, location_lng)

    open_now = is_open_now(keyword, location)
    # open_now is True, False, or None
    if open_now:
        open_now = "Open now"
    elif open_now is None:
        open_now = "Open now unknown"
    else:
        open_now = "Closed"

    # Add open now info to dictionary
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
        business['timestamp'] = arrow.get(wait_info.timestamp).humanize()
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
        business['timestamp'] = "N/A"
        business['timestamp_value'] = datetime(2000, 2, 2)


def sorted_result(result, sort_value):
    """Returns result sorted by the selected value."""

    # Sort by recently reported
    if sort_value == "recently_reported":
        result.sort(key=lambda business: business['timestamp_value'], reverse=True)

    # Sort by shortest wait time
    if sort_value == "wait_time":
        result.sort(key=lambda business: business['quoted_wait_time'])

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
            if (business['quoted_wait_time'] != "Not available" and
                    business['quoted_wait_time'] <= 15):
                new_result.append(business)
        result = new_result

    # Filter by <=30 min wait
    if "30_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if (business['quoted_wait_time'] != "Not available" and
                    business['quoted_wait_time'] <= 30):
                new_result.append(business)
        result = new_result

    # Filter by <=45 min wait
    if "45_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if (business['quoted_wait_time'] != "Not available" and
                    business['quoted_wait_time'] <= 45):
                new_result.append(business)
        result = new_result

    # Filter by <=60 min wait
    if "60_min_wait" in selected_filters:
        new_result = []
        for business in result:
            if (business['quoted_wait_time'] != "Not available" and
                    business['quoted_wait_time'] <= 60):
                new_result.append(business)
        result = new_result

    return result


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run()
