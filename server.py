from flask import Flask, render_template, request
from yelpapi import YelpAPI
import os
import pprint


app = Flask(__name__)


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


@app.route("/search")
def display_search_results():
    """Display search results."""

    return render_template("results.html")


##################
#### YELP API ####

consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)
search_results = yelp_api.search_query(term='Sanraku', location='san francisco, ca', limit=5)

# pprint.pprint(search_results)

name = search_results['businesses'][0]['name']
print "NAME", name
business_id = search_results['businesses'][0]['id']
print "BUSINESS ID", business_id
review_count = search_results['businesses'][0]['review_count']
print "REVIEW COUNT", review_count
rating = search_results['businesses'][0]['rating']
print "RATING", rating

# business_results = yelp_api.business_query(id=business_id)
# print "BUSINESS RESULTS\n"
# pprint.pprint(business_results)




if __name__ == "__main__":
    app.debug = True

    app.run()
