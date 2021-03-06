"""Yelp API Set Up"""

import os
from yelpapi import YelpAPI

CONSUMER_KEY = os.environ['YELP_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['YELP_CONSUMER_SECRET']
TOKEN = os.environ['YELP_TOKEN']
TOKEN_SECRET = os.environ['YELP_TOKEN_SECRET']

yelp = YelpAPI(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET)
