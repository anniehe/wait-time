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
    phone_number = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide useful representation of reported wait when printed."""

        return "<WaitTime wait_time_id=%s yelp_id=%s quoted_minutes=%s>" % (
            self.wait_time_id, self.yelp_id, self.quoted_minutes)


##############################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///wait'):
    """Connect database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLAlCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
