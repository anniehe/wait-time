import requests
import os

key = os.environ['GOOGLE_SERVER_KEY']


def get_place_id(keyword, location):
    """Get place_id from Google Places API for a business."""

    ### TEXTSEARCH ###
    payload = {'key': key,
               'query': keyword,
               'location': location,
               'radius': '500'}

    r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=payload)

    ### NEARBY SEARCH ###
    # payload = {'key': key,
    #            'keyword': keyword,
    #            'location': location,
    #            'radius': '500'}

    # r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=payload)

    place_results = r.json()

    if place_results.get('results'):
        # print place_results
        place_id = place_results['results'][0]['place_id']
        # print place_results['results'][0]['name']
        return place_id

    elif place_results['status'] == "OVER_QUERY_LIMIT":
        raise Exception('Over query limit...')


def get_opening_hours_info(place_id):
    """Get information on business hours and if open now from Google Places API."""

    payload = {'key': key,
               'placeid': place_id}

    r = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=payload)

    place_details = r.json()

    # print "PLACE DETAILS", place_details

    # If there is a result and there is information on opening hours, return those values
    if place_details.get('result'):
        if place_details['result'].get('opening_hours'):

            # opening_hours is a list
            opening_hours = place_details['result']['opening_hours']['weekday_text']

            # open_now is True or False
            open_now = place_details['result']['opening_hours']['open_now']

            # print "OPENING HOURS", opening_hours
            # print "OPEN NOW", open_now

            return [opening_hours, open_now]
        else:
            return None

    else:
        print place_details
        raise Exception('No results for place_id %s' % (place_id))
