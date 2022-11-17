from datetime import datetime

from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show_id = db.relationship('Show', backref='show_venue', uselist=False)

    def __repr__(self):
        return f'<Venue {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'address: {self.address}, phone: {self.phone}, genres: {self.genres}, ' \
               f'image_link: {self.image_link}, facebook_link: {self.facebook_link}, ' \
               f'website_link: {self.website_link}, seeking_talent: {self.seeking_talent}, ' \
               f'seeking_description: {self.seeking_description}>'


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show_id = db.relationship('Show', backref='show_artists')

    def __repr__(self):
        return f'<Artist {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'phone: {self.phone}, genres: {self.genres}, ' \
               f'image_link: {self.image_link}, facebook_link: {self.facebook_link}, ' \
               f'website_link: {self.website_link}, seeking_venue: {self.seeking_venue}, ' \
               f'seeking_description: {self.seeking_description}>'


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return f'<Show {self.id}, artist: {self.artist_id}, venue: {self.venue_id}, ' \
               f'start_time: {self.start_time}>'
