# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import sys
from logging import Formatter, FileHandler

import babel
import dateutil.parser
# import sqlalchemy
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import cast, Date
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from datetime import date

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    # __tablename__ = 'Venue'

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
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    show_id = db.relationship('Show', backref='show_venue', uselist=False)

    def __repr__(self):
        return f'<Venue {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'address: {self.address}, phone: {self.phone}, genres: {self.genres}, ' \
               f'image_link: {self.image_link}, facebook_link: {self.facebook_link}, ' \
               f'website_link: {self.website_link}, seeking_talent: {self.seeking_talent}, ' \
               f'seeking_description: {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    # __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    show_id = db.relationship('Show', backref='show_artists')

    def __repr__(self):
        return f'<Artist {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'phone: {self.phone}, genres: {self.genres}, ' \
               f'image_link: {self.image_link}, facebook_link: {self.facebook_link}, ' \
               f'website_link: {self.website_link}, seeking_venue: {self.seeking_venue}, ' \
               f'seeking_description: {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    # __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return f'<Show {self.id}, artist: {self.artist_id}, venue: {self.venue_id}, ' \
               f'start_time: {self.start_time}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# db.drop_all()
db.create_all()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    venue_city_groupings = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    print("Venue/City groupings => ", venue_city_groupings)

    venues_data = []

    for grouping in venue_city_groupings:
        # print("Venue city => ", grouping[0])
        venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == grouping[0]).all()
        grouping = grouping._asdict()  # Dictionary format of grouping.
        # print("Venues in city => ", grouping)
        venues_list = []
        for venue_in_city in venues_in_city:
            num_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(
                Show.venue_id == venue_in_city[0], db.cast(Show.start_time, db.Date) >= date.today()).count()
            # print("Show count for venue => ", num_shows)
            venue_in_city = venue_in_city._asdict()  # Dictionary format of venue_in_city.
            venue_in_city["num_upcoming_shows"] = num_shows  # Writing upcoming show count to object.
            # print("Appended => ", venue_in_city)
            venues_list.append(venue_in_city)  # Adding this venue to the list of venues per city.

        grouping["venues"] = venues_list  # Venues attribute for this city.
        print("Structured venues => ", grouping)
        venues_data.append(grouping)

    # print("All structured venues => ", venues_data)

    return render_template('pages/venues.html', areas=venues_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    selected_venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    past_shows = db.session.query(Show.artist_id, Artist.name.label('artist_name'),
                                  Artist.image_link.label('artist_image_link'), Show.start_time).join(Artist,
                                                                                                      Show.artist_id == Artist.id).filter(
        Show.venue_id == venue_id, db.cast(Show.start_time, db.Date) < date.today()).all()
    upcoming_shows = db.session.query(Show.artist_id, Artist.name.label('artist_name'),
                                      Artist.image_link.label('artist_image_link'), Show.start_time).join(Artist,
                                                                                                          Show.artist_id == Artist.id).filter(
        Show.venue_id == venue_id, db.cast(Show.start_time, db.Date) >= date.today()).all()
    past_shows_count = db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(
        Show.venue_id == venue_id, db.cast(Show.start_time, db.Date) < date.today()).count()
    upcoming_shows_count = db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(
        Show.venue_id == venue_id, db.cast(Show.start_time, db.Date) >= date.today()).count()

    # Aggregating data from the Venue, with their respective Shows data.
    data = {
        "id": selected_venue.id,
        "name": selected_venue.name,
        "genres": selected_venue.genres,
        "city": selected_venue.city,
        "state": selected_venue.state,
        "phone": selected_venue.phone,
        "seeking_talent": selected_venue.seeking_talent,
        "image_link": selected_venue.image_link,
        "past_shows": [show._asdict() for show in past_shows],
        "upcoming_shows": [show._asdict() for show in upcoming_shows],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    body = {}
    form = VenueForm()
    try:
        # TODO: 1. Remember to validate the form fields (if form.validate():
        #  2. Also adopt this pattern (name = form.name.data))
        #  3. And show errors if they come up

        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        address = request.get_json()['address']
        phone = request.get_json()['phone']
        genres = request.get_json()['genres']
        image_link = request.get_json()['image_link']
        facebook_link = request.get_json()['facebook_link']
        website_link = request.get_json()['website_link']
        seeking_talent = form.seeking_talent.data
        seeking_description = request.get_json()['seeking_description']

        print("Venue form request => ", request.get_json())
        print("Venue Form (WTF) => ", form.seeking_talent.data)

        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )

        print("Venue Form (Seeking talent) => ", venue.seeking_talent)

        db.session.add(venue)
        db.session.commit()

        body['name'] = venue.name
        body['city'] = venue.city
        body['state'] = venue.state
        body['address'] = venue.address
        body['phone'] = venue.phone
        body['genres'] = venue.genres
        body['image_link'] = venue.image_link
        body['facebook_link'] = venue.facebook_link
        body['website_link'] = venue.website_link
        body['seeking_talent'] = venue.seeking_talent
        body['seeking_description'] = venue.seeking_description

        # print("Venue object => ", request.get_json()['seeking_talent'])
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    db_artists = db.session.query(Artist).all()

    # for artist in db_artists:
    #     print("Artist in DB: => ", artist.name)

    return render_template('pages/artists.html', artists=db_artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    form = request.form
    if "search_term" in form.keys():
        search_value = form['search_term']
        # print("Artist search term => ", request.form.get("search_term"))
        results = db.session.query(Artist.id, Artist.name, ).filter(Artist.name.ilike("%" + search_value + "%")).all()
        results_count = db.session.query(Artist).filter(Artist.name.ilike("%" + search_value + "%")).count()

        data = []  # Final list of responses.

        # Looping through results to get number of shows per artist.
        for result in results:
            # print("Result in results => ", result.name)
            num_upcoming_shows = db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(
                Show.artist_id == result.id, db.cast(Show.start_time, db.Date) >= date.today()).count()
            data_item = {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": num_upcoming_shows,
            }
            data.append(data_item)

        response = {
            "count": results_count,
            "data": data
        }  # Response object

        # print("Artist search response data => ", response)

        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Showing the artist page with the given artist_id.
    db_artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    past_shows = db.session.query(Show.venue_id, Venue.name.label('venue_name'),
                                  Venue.image_link.label('venue_image_link'), Show.start_time).join(Venue,
                                                                                                    Show.venue_id == Venue.id).filter(
        Show.artist_id == artist_id, db.cast(Show.start_time, db.Date) < date.today()).all()
    upcoming_shows = db.session.query(Show.venue_id, Venue.name.label('venue_name'),
                                      Venue.image_link.label('venue_image_link'), Show.start_time).join(Venue,
                                                                                                        Show.venue_id == Venue.id).filter(
        Show.artist_id == artist_id, db.cast(Show.start_time, db.Date) >= date.today()).all()

    past_shows_count = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(
        Show.artist_id == artist_id, db.cast(Show.start_time, db.Date) < date.today()).count()
    upcoming_shows_count = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(
        Show.artist_id == artist_id, db.cast(Show.start_time, db.Date) >= date.today()).count()

    # Aggregating data from the Artist, with their respective Shows data.
    data = {
        "id": db_artist.id,
        "name": db_artist.name,
        "genres": db_artist.genres,
        "city": db_artist.city,
        "state": db_artist.state,
        "phone": db_artist.phone,
        "seeking_venue": db_artist.seeking_venue,
        "image_link": db_artist.image_link,
        "past_shows": [show._asdict() for show in past_shows],
        "upcoming_shows": [show._asdict() for show in upcoming_shows],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    # print("DB Artist => ", data)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = db.session.query(Artist.id, Artist.name, Artist.genres, Artist.city, Artist.state, Artist.phone,
                              Artist.website_link, Artist.facebook_link, Artist.seeking_venue,
                              Artist.seeking_description, Artist.image_link).filter(
        Artist.id == artist_id).first()

    # TODO: populate form with fields from artist with ID <artist_id>
    print("Edit artist GET request => ", artist)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    existing_artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    # TODO: if artist_form.validate():

    error = False
    artist_body = {}
    artist_form = ArtistForm()

    print("Artist form name =>", artist_form.name.data)

    try:
        existing_artist.name = request.get_json()['name']
        existing_artist.city = request.get_json()['city']
        existing_artist.state = request.get_json()['state']
        existing_artist.phone = request.get_json()['phone']
        existing_artist.genres = request.get_json()['genres']
        existing_artist.image_link = request.get_json()['image_link']
        existing_artist.facebook_link = request.get_json()['facebook_link']
        existing_artist.website_link = request.get_json()['website_link']
        existing_artist.seeking_venue = artist_form.seeking_venue.data
        existing_artist.seeking_description = request.get_json()['seeking_description']

        print("Saving existing artist => ", existing_artist.name)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(artist_body)

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    artist_body = {}
    artist_form = ArtistForm()

    try:
        # TODO: 1. Remember to validate the form fields (if form.validate():
        #  2. Also adopt this pattern (name = form.name.data))
        #  3. And show errors if they come up

        artist_name = request.get_json()['name']
        artist_city = request.get_json()['city']
        artist_state = request.get_json()['state']
        artist_phone = request.get_json()['phone']
        artist_genres = request.get_json()['genres']
        artist_image_link = request.get_json()['image_link']
        artist_facebook_link = request.get_json()['facebook_link']
        artist_website_link = request.get_json()['website_link']
        artist_seeking_venue = artist_form.seeking_venue.data
        artist_seeking_description = request.get_json()['seeking_description']

        print("Artist form request => ", request.get_json())
        print("Artist Form (WTF) => ", artist_form.website_link.data)

        artist = Artist(
            name=artist_name,
            city=artist_city,
            state=artist_state,
            phone=artist_phone,
            genres=artist_genres,
            image_link=artist_image_link,
            facebook_link=artist_facebook_link,
            website_link=artist_website_link,
            seeking_venue=artist_seeking_venue,
            seeking_description=artist_seeking_description
        )

        print("Artist Form (Seeking venue) => ", artist_form.name.data)

        db.session.add(artist)
        db.session.commit()

        artist_body['name'] = artist.name,
        artist_body['city'] = artist.city,
        artist_body['state'] = artist.state,
        artist_body['phone'] = artist.phone,
        artist_body['genres'] = artist.genres,
        artist_body['image_link'] = artist.image_link,
        artist_body['facebook_link'] = artist.facebook_link,
        artist_body['website_link'] = artist.website_link,
        artist_body['seeking_venue'] = artist.seeking_venue,
        artist_body['seeking_description'] = artist.seeking_description

        print("Artist object => ", artist)

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(artist_body)

        # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    error = False
    body = {}
    form = ShowForm()

    try:
        # TODO: 1. Remember to validate the form fields (if form.validate():
        #  2. Also adopt this pattern (name = form.name.data))
        #  3. And show errors if they come up

        venue_id = request.get_json()['venue_id']
        artist_id = request.get_json()['artist_id']
        start_time = request.get_json()['start_time']

        print("Show form request => ", request.get_json())
        print("Show Form (WTF) => ", form.start_time)

        show = Show(
            venue_id=venue_id,
            artist_id=artist_id,
            start_time=start_time
        )

        db.session.add(show)
        db.session.commit()

        body['venue_id'] = show.venue_id
        body['artist_id'] = show.artist_id
        body['start_time'] = show.start_time

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

# # venues = Venue.query("Venue.city").group_by(Venue.city).all()
#
# shows = db.session.query(Show).filter(Show.start_time > '2022-09-01 17:03:06').count()  # Seems correct
# filtered_venues = db.session.query(Venue.id, Venue.name, shows).join(Show, Venue.show_id).all()  # Seems correct
#
# # venues_agg = db.func.array_agg(Venue.id, type_=db.ARRAY(db.Integer)).label('venuez')
#
# # venues = db.session.query(Venue.city, Venue.state,
# #                           db.func.array(filtered_venues), Venue.id).group_by(
# #     Venue.city, Venue.state, Venue.id).all()
#
# venues = db.session.query(Venue.city, Venue.state,
#                           db.func.json_agg(filtered_venues).label("vn"), Venue.id).group_by(
#     Venue.city, Venue.state, Venue.id).all()
