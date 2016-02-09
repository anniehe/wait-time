from flask import Flask, render_template, request
from yelp_api import *

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

    search_results = yelp_search(search_term, location_term)
    result = search_results['businesses']

    return render_template("results.html", result=result)


if __name__ == "__main__":
    app.debug = True

    app.run()
