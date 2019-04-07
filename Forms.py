from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, IntegerField, RadioField, DateField
from wtforms.validators import InputRequired, NumberRange, Length
import re

class query_players_Form(FlaskForm):

    name = StringField('Name of the player:', validators=[InputRequired(),Length(min=1, max=39)])
    submit = SubmitField('Search')

class query_teams_Form(FlaskForm):

    name = StringField('Name of the team:', validators=[InputRequired(),Length(min=1, max=39)])
    submit = SubmitField('Search')

class query_games_Form(FlaskForm):

    home_name = StringField('Name of the home team:', validators=[InputRequired(),Length(min=1, max=39)])
    away_name = StringField('Name of the away team:', validators=[InputRequired(),Length(min=1, max=39)])
    submit = SubmitField('Search')

class query_venues_Form(FlaskForm):

    name = StringField('Name of the venue:', validators=[InputRequired(),Length(min=1, max=39)])
    submit = SubmitField('Search')

class add_player_Form(FlaskForm):

    player_name = StringField('Name of the player:', validators=[InputRequired(),Length(min=1, max=39)])
    team_name = StringField('Name of the team:', validators=[InputRequired(),Length(min=1, max=39)])
    submit = SubmitField('Add')

class add_game_Form(FlaskForm):
    date = DateField('Date of the game:',validators=[InputRequired()], format='%m/%d/%y',
                          render_kw={'placeholder': 'e.g.12/31/99'})
    home_teamname = StringField('Name of the home team:', validators=[InputRequired(),Length(min=1, max=39)])
    away_teamname = StringField('Name of the away team:', validators=[InputRequired(),Length(min=1, max=39)])
    winner = RadioField(u'Winner:',
                          choices=[('home', 'Home team'),
                                   ('away', 'Away team')], validators=[InputRequired()])
    home_runnumber = IntegerField('Run number of home team', validators=[InputRequired()])
    home_errornumber = IntegerField('Error number of home team', validators=[InputRequired()])
    home_hitnumber = IntegerField('Hit number of home team', validators=[InputRequired()])

    away_runnumber = IntegerField('Run number of away team', validators=[InputRequired()])
    away_errornumber = IntegerField('Error number of away team', validators=[InputRequired()])
    away_hitnumber = IntegerField('Hit number of away team', validators=[InputRequired()])

    weather = SelectField(u'Weather:',
                            choices=[('In Dome', 'In Dome'),
                                     ('Sunny', 'Sunny'),
                                     ('Cloudy', 'Cloudy'),
                                     ('Rain', 'Rain'),
                                     ('Drizzle', 'Drizzle'),
                                     ('Overcast', 'Overcast'),
                                     ('Unknown', 'Unknown')
                                     ], validators=[InputRequired()])
    venue = StringField('Name of the venue:', validators=[InputRequired(),Length(min=1, max=39)])
    day_or_night = RadioField(u'Day or night:',
                          choices=[('D', 'Day'),
                                   ('N', 'Night')], validators=[InputRequired(),Length(min=1, max=9)])
    submit = SubmitField('Add')
