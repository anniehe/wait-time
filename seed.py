from model import WaitTime, connect_to_db, db
from server import app
from datetime import datetime


def load_wait_times():
    """Load some wait times into database."""

    wait1 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=3,
                     quoted_minutes=120,
                     parties_ahead=10,
                     timestamp=datetime(2016, 2, 12, 21, 55))

    wait2 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=2,
                     quoted_minutes=90,
                     parties_ahead=6,
                     timestamp=datetime(2016, 2, 12, 21, 55))

    wait3 = WaitTime(yelp_id="sanraku-san-francisco-4",
                     party_size=6,
                     quoted_minutes=60,
                     parties_ahead=5,
                     timestamp=datetime(2016, 2, 12, 20, 50))

    wait4 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=3,
                     quoted_minutes=20,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 12, 19, 40))

    wait5 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=4,
                     quoted_minutes=30,
                     parties_ahead=5,
                     timestamp=datetime(2016, 2, 12, 22, 1))

    wait6 = WaitTime(yelp_id="nara-sushi-san-francisco",
                     party_size=2,
                     quoted_minutes=90,
                     parties_ahead=6,
                     timestamp=datetime(2016, 2, 12, 22, 15))

    wait7 = WaitTime(yelp_id="ryokos-san-francisco",
                     party_size=2,
                     quoted_minutes=45,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 13, 2, 1))

    wait8 = WaitTime(yelp_id="ebisu-san-francisco",
                     party_size=2,
                     quoted_minutes=45,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 12, 20, 30),
                     still_waiting=False)

    wait9 = WaitTime(yelp_id="akikos-restaurant-san-francisco",
                     party_size=2,
                     quoted_minutes=75,
                     parties_ahead=4)

    db.session.add(wait1)
    db.session.add(wait2)
    db.session.add(wait3)
    db.session.add(wait4)
    db.session.add(wait5)
    db.session.add(wait6)
    db.session.add(wait7)
    db.session.add(wait8)
    db.session.add(wait9)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_wait_times()
