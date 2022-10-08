from datetime import datetime
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

from Genre import Genre
from State import State


class ShowForm(FlaskForm):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField('start_time', validators=[DataRequired()], default=datetime.today())


class VenueForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.choices())
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.choices())
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')

    seeking_talent = BooleanField('seeking_talent', default=False,
                                  validators=[AnyOf([True, False])])

    seeking_description = StringField('seeking_description')


class ArtistForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.choices())
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.choices)
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')

    seeking_venue = BooleanField('seeking_venue', default=False, validators=[AnyOf([True, False])])

    seeking_description = StringField('seeking_description')
