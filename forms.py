from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, FileField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired
from wtforms.widgets import TextArea, CheckboxInput

class UserAddForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class UserInfoForm(FlaskForm):
    image_url = StringField("Image URL")
    bio = StringField("Type bio here!", widget=TextArea())
    website = StringField("Website URL")
    region_id = SelectField("Where is this job?", coerce=int, validators=[InputRequired()])
    instrument_id = SelectField("What is your primary instrument", coerce=int)
    genre_id = SelectField("Whatkind of music do you play?", coerce=int)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class EventForm(FlaskForm):
    title = StringField("What is the event called", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    address = StringField("What is the Address of the event?", validators=[InputRequired()])
    date = DateTimeLocalField("Date of Event", validators=[InputRequired()])
    region_id = SelectField("Where is this job?", coerce=int, validators=[InputRequired()])
    genre = StringField("What type of music will you play?", validators=[InputRequired()])


class JobForm(FlaskForm):
    title = StringField("What is the event called", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    pay = FloatField("How does the gig pay(in dollars)", validators=[InputRequired()])
    date = DateTimeLocalField("Date of Event", validators=[InputRequired()]) 
    region_id = SelectField("Where is this job?", coerce=int, validators=[InputRequired()])
    genre = StringField("What type of music will you play?", validators=[InputRequired()])

class AddRegion(FlaskForm):
    city = StringField("City", validators=[InputRequired()])
    county = StringField("County", validators=[InputRequired()])
    state = StringField("State", validators=[InputRequired()])