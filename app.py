# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import sys
from datetime import date
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from forms import *

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


# TODO: connect to a local postgresql database

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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
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
    # print("Venue/City groupings => ", venue_city_groupings)

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
        # print("Structured venues => ", grouping)
        venues_data.append(grouping)

    # print("All structured venues => ", venues_data)

    return render_template('pages/venues.html', areas=venues_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    form = request.form
    if "search_term" in form.keys():
        search_value = form['search_term']
        # print("Artist search term => ", request.form.get("search_term"))
        results = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike("%" + search_value + "%")).all()
        results_count = db.session.query(Venue).filter(Venue.name.ilike("%" + search_value + "%")).count()

        data = []  # Final list of responses.

        # Looping through results to get number of shows per venue.
        for result in results:
            # print("Result in results => ", result.name)
            num_upcoming_shows = db.session.query(Show).join(Venue, Show.artist_id == Venue.id).filter(
                Show.venue_id == result.id, db.cast(Show.start_time, db.Date) >= date.today()).count()
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
        "address": selected_venue.address,
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
    # For inserting form data as a new Venue record in the db.

    error = False
    form = VenueForm()

    print("Venue creation form ==== ", form.data)

    if form.validate_on_submit():
        print("VALIDATE CREATE VENUE FORM ************")

        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            address = form.address.data
            phone = form.phone.data
            genres = form.genres.data
            image_link = form.image_link.data
            facebook_link = form.facebook_link.data
            website_link = form.website_link.data
            seeking_talent = form.seeking_talent.data
            seeking_description = form.seeking_description.data

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

            db.session.add(venue)
            db.session.commit()

            # On successful db insert, flash success
            flash('Artist ' + venue.name + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            # On unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
            abort(400)
        else:

            return render_template('pages/home.html')
    else:

        return render_template('forms/new_venue.html', form=form)


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

    # Populating form with fields from artist with ID <artist_id>
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
    # Takes values from the form submitted, and updates the existing
    # artist record with ID <artist_id> using the form attributes.

    existing_artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    error = False
    form = ArtistForm()

    print("Artist form ==== ", form.data)

    if form.validate_on_submit():
        print("VALID ********")
        try:
            existing_artist.name = form.name.data
            existing_artist.city = form.city.data
            existing_artist.state = form.state.data
            existing_artist.phone = form.phone.data
            existing_artist.genres = form.genres.data
            existing_artist.image_link = form.image_link.data
            existing_artist.facebook_link = form.facebook_link.data
            existing_artist.website_link = form.website_link.data
            existing_artist.seeking_venue = form.seeking_venue.data
            existing_artist.seeking_description = form.seeking_description.data

            print("Saving existing artist => ", existing_artist)
            db.session.commit()

            return redirect(url_for('show_artist', artist_id=artist_id))
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            abort(400)
        else:
            return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        print("ARTIST EDIT FORM VALIDATION ERRORS *> ", form.errors)
        return render_template('forms/edit_artist.html', form=form, artist=existing_artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = db.session.query(Venue.id, Venue.name, Venue.genres, Venue.city, Venue.state, Venue.address, Venue.phone,
                             Venue.website_link, Venue.facebook_link, Venue.seeking_talent,
                             Venue.seeking_description, Venue.image_link).filter(
        Venue.id == venue_id).first()

    # Populating form with values from venue with ID <venue_id>
    print("Edit venue GET request => ", venue)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Takes values from the form submitted, and update existing
    # venue record with ID <venue_id> using the form attributes.

    existing_venue = db.session.query(Venue).filter(Venue.id == venue_id).first()

    error = False
    form = VenueForm()

    print("Venue form ====", form.name.data)

    if form.validate_on_submit():
        print("VALID EDIT VENUE FORM **********")

        try:
            existing_venue.name = form.name.data
            existing_venue.city = form.city.data
            existing_venue.state = form.state.data
            existing_venue.address = form.address.data
            existing_venue.phone = form.phone.data
            existing_venue.genres = form.genres.data
            existing_venue.image_link = form.image_link.data
            existing_venue.facebook_link = form.facebook_link.data
            existing_venue.website_link = form.website_link.data
            existing_venue.seeking_talent = form.seeking_talent.data
            existing_venue.seeking_description = form.seeking_description.data

            print("Saving existing artist => ", existing_venue)
            db.session.commit()

            return redirect(url_for('show_venue', venue_id=venue_id))
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            abort(400)
        else:
            return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        print("VENUE EDIT FORM VALIDATION ERRORS *> ", form.errors)
        return render_template('forms/edit_venue.html', form=form, venue=existing_venue)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Called upon submitting the new artist listing form
    # Inserts form data as a new Venue record in the db.

    error = False
    form = ArtistForm()

    print("Artist creation form ==== ", form.data)

    if form.validate_on_submit():
        print("VALID CREATE ARTIST FORM **********")

        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            phone = form.phone.data
            genres = form.genres.data
            image_link = form.image_link.data
            facebook_link = form.facebook_link.data
            website_link = form.website_link.data
            seeking_venue = form.seeking_venue.data
            seeking_description = form.seeking_description.data

            artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                image_link=image_link,
                facebook_link=facebook_link,
                website_link=website_link,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description
            )

            db.session.add(artist)
            db.session.commit()

            # On successful db insert, flash success
            flash('Artist ' + artist.name + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            # On unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
            abort(400)
        else:

            return render_template('pages/home.html')
    else:

        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []
    shows = db.session.query(Show).all()

    for show in shows:
        venue = db.session.query(Venue.name).filter(Venue.id == show.id).first()
        # print("Show me the venue => ", venue)

        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.id).first()
        # print("Show me the artist => ", artist)

        show_obj = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": "",
            "artist_image_link": "",
            "start_time": show.start_time
        }
        data.append(show_obj)

    # print("All the shows => ", data)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # For show form rendering.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Called to create new shows in the db, upon submitting new show listing form.
    # Also inserts form data as a new Show record in the db.

    error = False
    body = {}

    try:
        venue_id = request.get_json()['venue_id']
        artist_id = request.get_json()['artist_id']
        start_time = request.get_json()['start_time']

        show = Show(
            venue_id=venue_id,
            artist_id=artist_id,
            start_time=start_time
        )

        form = ShowForm(obj=show)

        print("Show Form (Validated) => ", form.validate())
        print("Show Form (WTF) => ", form.data)
        print("Show Obj => ", show)

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
        # On unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show ' + show.name + ' could not be listed.')

        abort(400)
    else:
        # On successful db insert, flash success
        flash('Show ' + str(show.id) + ' was successfully listed!')

        return jsonify(body)

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
