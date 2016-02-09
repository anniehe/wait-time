from flask import Flask, render_template, request
from yelpapi import YelpAPI
import os

app = Flask(__name__)


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


@app.route("/search")
def display_search_results():
    """Display search results."""

    search_term = request.args.get('keyword')

    location_term = request.args.get('location')
    if not location_term:
        location_term = 'San Francisco'

    search_results = yelp_api.search_query(term=search_term,
                                           location=location_term,
                                           category_filter='food,restaurants')
    # result is the list of businesses
    result = search_results['businesses']

    return render_template("results.html", result=result)


### YELP API ###

consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)




if __name__ == "__main__":
    app.debug = True

    app.run()
