"""Functions to process results"""

from model import WaitTime
from google_api import is_open_now
from datetime import datetime
import arrow


def add_open_status(restaurant):
    """Add restaurant's open status at the current time to the its dictionary.

        >>> mock_restaurant = { "rating": 4.0, "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png", "review_count": 1983, "name": "Ryoko's", "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png", "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg", "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg", "display_phone": "+1-415-775-1028", "id": "ryokos-san-francisco", "location": { "city": "San Francisco", "postal_code": "94102", "address": [ "619 Taylor St" ], "coordinate": { "latitude": 37.788008004427, "longitude": -122.411782890558 }, "state_code": "CA" }}
        >>> add_open_status(mock_restaurant)
    """

    # Find matching Google Places open status info for the Yelp restaurant result
    name = restaurant['name']
    address = restaurant['location']['address'][0]
    city = restaurant['location']['city']
    location_lat = restaurant['location']['coordinate']['latitude']
    location_lng = restaurant['location']['coordinate']['longitude']

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
    restaurant['open_now'] = open_now


def add_wait_info(restaurant):
    """Add restaurant's wait time information from database to its dictionary."""

    yelp_id = restaurant['id']

    # Find the most recent wait time info for a restaurant from the database.
    # For records with the same timestamp, fetch the largest quoted wait time.
    wait_info = (WaitTime.query.filter_by(yelp_id=yelp_id)
                 .order_by(WaitTime.timestamp.desc(), WaitTime.quoted_minutes.desc())
                 .first()
                 )

    # Add wait time info to dictionary
    if wait_info:
        restaurant['quoted_wait_time'] = wait_info.quoted_minutes
        restaurant['timestamp'] = arrow.get(wait_info.timestamp).humanize()
        restaurant['timestamp_value'] = wait_info.timestamp

        if wait_info.party_size:
            restaurant['party_size'] = wait_info.party_size
        else:
            restaurant['party_size'] = "N/A"

        if wait_info.parties_ahead:
            restaurant['parties_ahead'] = wait_info.parties_ahead
        else:
            restaurant['parties_ahead'] = "N/A"

    else:
        restaurant['quoted_wait_time'] = "Not available"
        restaurant['party_size'] = "N/A"
        restaurant['parties_ahead'] = "N/A"
        restaurant['timestamp'] = "N/A"
        restaurant['timestamp_value'] = datetime(2000, 2, 2)


def sorted_result(result, sort_value):
    """Returns result sorted by the selected value."""

    # Sort by recently reported
    if sort_value == "recently_reported":
        result.sort(key=lambda restaurant: restaurant['timestamp_value'], reverse=True)

    # Sort by shortest wait time
    if sort_value == "wait_time":
        result.sort(key=lambda restaurant: restaurant['quoted_wait_time'])

    # Sort by highest rating
    if sort_value == "rating":
        result.sort(key=lambda restaurant: restaurant['rating'], reverse=True)

    # Sort by most reviews
    if sort_value == "review_count":
        result.sort(key=lambda restaurant: restaurant['review_count'], reverse=True)

    return result


def filtered_result(result, selected_filters):
    """Returns filtered result."""

    # Filter by open now
    if "open_now" in selected_filters:
        new_result = []
        for restaurant in result:
            if restaurant['open_now'] == "Open now":
                new_result.append(restaurant)
        result = new_result

    # Filter by <=15 min wait
    if "15_min_wait" in selected_filters:
        new_result = []
        for restaurant in result:
            if (restaurant['quoted_wait_time'] != "Not available" and
                    restaurant['quoted_wait_time'] <= 15):
                new_result.append(restaurant)
        result = new_result

    # Filter by <=30 min wait
    if "30_min_wait" in selected_filters:
        new_result = []
        for restaurant in result:
            if (restaurant['quoted_wait_time'] != "Not available" and
                    restaurant['quoted_wait_time'] <= 30):
                new_result.append(restaurant)
        result = new_result

    # Filter by <=45 min wait
    if "45_min_wait" in selected_filters:
        new_result = []
        for restaurant in result:
            if (restaurant['quoted_wait_time'] != "Not available" and
                    restaurant['quoted_wait_time'] <= 45):
                new_result.append(restaurant)
        result = new_result

    # Filter by <=60 min wait
    if "60_min_wait" in selected_filters:
        new_result = []
        for restaurant in result:
            if (restaurant['quoted_wait_time'] != "Not available" and
                    restaurant['quoted_wait_time'] <= 60):
                new_result.append(restaurant)
        result = new_result

    return result
