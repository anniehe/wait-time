from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# This is the connection to the PostgreSQL database
db = SQLAlchemy()


##############################################################################
# Model definitions

class WaitTime(db.Model):
    """Wait time information."""

    __tablename__ = "wait_times"

    wait_time_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    yelp_id = db.Column(db.String(200), db.ForeignKey("restaurants.yelp_id"))
    party_size = db.Column(db.Integer, nullable=True)
    quoted_minutes = db.Column(db.Integer, nullable=False)
    parties_ahead = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=func.utc_timestamp())

    restaurant = db.relationship("Restaurant",
                                 backref=db.backref("wait_times"))

    def __repr__(self):
        """Show information about the reported wait."""

        return "<WaitTime wait_time_id=%s yelp_id=%s quoted_minutes=%s>" % (
            self.wait_time_id, self.yelp_id, self.quoted_minutes)


class Restaurant(db.Model):
    """Restaurant from Yelp."""

    __tablename__ = "restaurants"

    yelp_id = db.Column(db.String(200), primary_key=True)
    restaurant_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Show information about the restaurant."""

        return "<Restaurant yelp_id=%s restaurant_name=%s rating=%s review_count=%s>" % (
            self.yelp_id, self.restaurant_name, self.rating, self.review_count)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wait'
    app.config['SQLAlCHEMY_ECHO'] = True
    # If want to tracking modifications, set it to True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
