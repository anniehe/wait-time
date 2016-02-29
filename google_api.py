import requests
import os

BROWSER_KEY = os.environ['GOOGLE_BROWSER_KEY']
SERVER_KEY = os.environ['GOOGLE_SERVER_KEY']


def is_open_now(keyword, location):
    """Given the keyword and location, returns a restaurant's open status (boolean), if available."""

    payload = {'key': SERVER_KEY,
               'query': keyword,
               'location': location,
               'radius': '500'}

    r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json",
                     params=payload)

    place_results = r.json()

    if place_results.get('results'):
        if place_results['results'][0].get('opening_hours'):
            # open_now is a boolean value indicating if the place is open at the current time
            open_now = place_results['results'][0]['opening_hours']['open_now']
            return open_now
