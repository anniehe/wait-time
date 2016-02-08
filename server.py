from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/")
def index():
    """Homepage."""

    return render_template("home.html")


@app.route("/search")
def display_search_results():
    """Display search results."""

    return render_template("results.html")


if __name__ == "__main__":
    app.debug = True

    app.run()
