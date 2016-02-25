from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This is the connection to the PostgreSQL database
db = SQLAlchemy()


##############################################################################
# Model definitions

class WaitTime(db.Model):
    """Wait time information."""

    __tablename__ = "wait_times"

    wait_time_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    yelp_id = db.Column(db.String(200), nullable=False)
    party_size = db.Column(db.Integer, nullable=True)
    parties_ahead = db.Column(db.Integer, nullable=True)
    quoted_minutes = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_time = db.Column(db.DateTime, nullable=False)
    phone_number = db.Column(db.String(100), nullable=True)
    still_waiting = db.Column(db.Boolean, default=True)
    msg_sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Provide useful representation of reported wait when printed."""

        return "<WaitTime wait_time_id=%s yelp_id=%s quoted_minutes=%s>" % (
            self.wait_time_id, self.yelp_id, self.quoted_minutes)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wait'
    app.config['SQLAlCHEMY_ECHO'] = True
    # If want to track modifications, set it to True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
