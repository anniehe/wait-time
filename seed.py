"""Seed sample data for database"""

from model import WaitTime, connect_to_db, db
from server import app
from datetime import datetime


def load_wait_times():
    """Load sample wait times into database."""

    wait1 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=3,
                     parties_ahead=10,
                     quoted_minutes=120,
                     timestamp=datetime(2016, 2, 25, 21, 55))

    wait2 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=2,
                     parties_ahead=6,
                     quoted_minutes=90,
                     timestamp=datetime(2016, 2, 25, 21, 55))

    wait3 = WaitTime(yelp_id="sanraku-san-francisco-4",
                     party_size=6,
                     parties_ahead=5,
                     quoted_minutes=60,
                     timestamp=datetime(2016, 2, 25, 20, 00))

    wait4 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=3,
                     parties_ahead=4,
                     quoted_minutes=20,
                     timestamp=datetime(2016, 2, 25, 19, 40))

    wait5 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=4,
                     parties_ahead=5,
                     quoted_minutes=30,
                     timestamp=datetime(2016, 2, 25, 22, 1))

    wait6 = WaitTime(yelp_id="nara-sushi-san-francisco",
                     party_size=2,
                     parties_ahead=6,
                     quoted_minutes=90)

    wait7 = WaitTime(yelp_id="ryokos-san-francisco",
                     party_size=2,
                     parties_ahead=4,
                     quoted_minutes=45,
                     timestamp=datetime(2016, 2, 26, 2, 1))

    wait8 = WaitTime(yelp_id="ebisu-san-francisco",
                     party_size=2,
                     parties_ahead=4,
                     quoted_minutes=45,
                     timestamp=datetime(2016, 2, 25, 20, 30))

    wait9 = WaitTime(yelp_id="akikos-restaurant-san-francisco",
                     party_size=2,
                     parties_ahead=4,
                     quoted_minutes=75,
                     timestamp=datetime(2016, 2, 25, 21, 15))

    db.session.add_all([wait1, wait2, wait3, wait4,
                        wait5, wait6, wait7, wait8,
                        wait9])

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_wait_times()
