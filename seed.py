from model import WaitTime, Restaurant, connect_to_db, db
from server import app
from datetime import datetime
from yelpapi import YelpAPI
import os


def load_restaurants():
    """Load some restaurants from Yelp into database."""

    search_results = yelp_api.search_query(term="Sanraku",
                                           location="San Francisco",
                                           category_filter="food,restaurants")

    result = search_results['businesses']

    for item in result:
        yelp_id = item['id']
        name = item['name']
        rating = item['rating']
        review_count = item['review_count']
        address = item['location']['address'][0]
        city = item['location']['city']
        state_code = item['location']['state_code']
        zip_code = item['location']['postal_code']

        restaurant = Restaurant(yelp_id=yelp_id,
                                restaurant_name=name,
                                rating=rating,
                                review_count=review_count,
                                address=address,
                                city=city,
                                state_code=state_code,
                                zip_code=zip_code)

        db.session.add(restaurant)

    db.session.commit()


def load_wait_times():
    """Load some wait times into database."""

    wait1 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size="2",
                     quoted_minutes="90",
                     parties_ahead="6",
                     timestamp=datetime(2016, 2, 11, 23, 45))

    wait2 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size="3",
                     quoted_minutes="120",
                     parties_ahead="10",
                     timestamp=datetime(2016, 2, 11, 23, 50))

    wait3 = WaitTime(yelp_id="sanraku-san-francisco-4",
                     party_size="6",
                     quoted_minutes="30",
                     parties_ahead="3",
                     timestamp=datetime(2016, 2, 11, 23, 51))

    wait4 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size="3",
                     quoted_minutes="20",
                     parties_ahead="4",
                     timestamp=datetime(2016, 2, 11, 23, 52))

    wait4 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size="4",
                     quoted_minutes="30",
                     parties_ahead="5",
                     timestamp=datetime(2016, 2, 11, 23, 53))

    wait5 = WaitTime(yelp_id="nara-sushi-san-francisco",
                     party_size="2",
                     quoted_minutes="45",
                     parties_ahead="6",
                     timestamp=datetime(2016, 2, 11, 23, 54))

    wait6 = WaitTime(yelp_id="ryokos-san-francisco",
                     party_size="2",
                     quoted_minutes="45",
                     parties_ahead="4",
                     timestamp=datetime(2016, 2, 12, 10, 54))

    db.session.add(wait1)
    db.session.add(wait2)
    db.session.add(wait3)
    db.session.add(wait4)
    db.session.add(wait5)
    db.session.add(wait6)
    db.session.commit()


### YELP API ###

consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_restaurants()
    load_wait_times()
