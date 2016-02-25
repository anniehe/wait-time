from model import WaitTime, connect_to_db, db
from server import app
from datetime import datetime, timedelta


def load_wait_times():
    """Load some wait times into database."""

    wait1 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=3,
                     quoted_minutes=120,
                     parties_ahead=10,
                     timestamp=datetime(2016, 2, 25, 21, 55),
                     estimated_time=datetime(2016, 2, 25, 23, 55))

    wait2 = WaitTime(yelp_id="sanraku-san-francisco-2",
                     party_size=2,
                     quoted_minutes=90,
                     parties_ahead=6,
                     timestamp=datetime(2016, 2, 25, 21, 55),
                     estimated_time=datetime(2016, 2, 25, 23, 25))

    wait3 = WaitTime(yelp_id="sanraku-san-francisco-4",
                     party_size=6,
                     quoted_minutes=60,
                     parties_ahead=5,
                     timestamp=datetime(2016, 2, 25, 20, 50),
                     estimated_time=datetime(2016, 2, 25, 21, 50))

    wait4 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=3,
                     quoted_minutes=20,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 25, 19, 40),
                     estimated_time=datetime(2016, 2, 25, 20, 0))

    wait5 = WaitTime(yelp_id="katana-ya-san-francisco",
                     party_size=4,
                     quoted_minutes=30,
                     parties_ahead=5,
                     timestamp=datetime(2016, 2, 25, 22, 1),
                     estimated_time=datetime(2016, 2, 25, 22, 31))

    wait6 = WaitTime(yelp_id="nara-sushi-san-francisco",
                     party_size=2,
                     quoted_minutes=90,
                     parties_ahead=6,
                     timestamp=datetime.utcnow(),
                     estimated_time=(datetime.utcnow() + timedelta(minutes=90)))

    wait7 = WaitTime(yelp_id="ryokos-san-francisco",
                     party_size=2,
                     quoted_minutes=45,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 26, 2, 1),
                     estimated_time=datetime(2016, 2, 26, 2, 46))

    wait8 = WaitTime(yelp_id="ebisu-san-francisco",
                     party_size=2,
                     quoted_minutes=45,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 25, 20, 30),
                     estimated_time=datetime(2016, 2, 25, 21, 15),
                     still_waiting=False)

    wait9 = WaitTime(yelp_id="akikos-restaurant-san-francisco",
                     party_size=2,
                     quoted_minutes=75,
                     parties_ahead=4,
                     timestamp=datetime(2016, 2, 25, 22, 15),
                     estimated_time=datetime(2016, 2, 25, 23, 30))

    db.session.add_all([wait1, wait2, wait3, wait4,
                        wait5, wait6, wait7, wait8,
                        wait9])

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()
    load_wait_times()
