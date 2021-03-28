from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, FileField, SelectMultipleField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired
from wtforms.widgets import TextArea, ListWidget, CheckboxInput

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
    region_id = SelectField("Where is this job?", coerce=int)

class UserFile(FlaskForm):
    cv = FileField("Attach your CV or Resume")

class UserInstrumentForm(FlaskForm):
    instrument_id = SelectMultipleField("What is your primary instrument", option_widget=CheckboxInput(), widget=ListWidget(prefix_label=True), coerce=int)

class UserGenreForm(FlaskForm):
    genre_id = SelectMultipleField("What kind of music do you play?", option_widget=CheckboxInput(), widget=ListWidget(prefix_label=True), coerce=int)

class UserSearchForm(FlaskForm):
    user_attributes = SelectField("Search Field", validators=[InputRequired()], choices=[('first_name', 'First Name'), ('last_name', 'Last Name'), ('email', 'Email')])
    search_info = StringField("What are you looking for?")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class EventForm(FlaskForm):
    title = StringField("What is the event called", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    address = StringField("What is the Address of the event?", validators=[InputRequired()])
    date = DateTimeLocalField("Date of Event", format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    region_id = SelectField("Where is this job?", coerce=int, validators=[InputRequired()])
    genre_id = SelectField("What type of music will you play?", coerce=int, validators=[InputRequired()])


class JobForm(FlaskForm):
    title = StringField("What is the event called", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    pay = FloatField("How much does the gig pay(in dollars)", validators=[InputRequired()])
    date = DateTimeLocalField("Date of Event", format='%Y-%m-%dT%H:%M', validators=[InputRequired()]) 
    region_id = SelectField("Where is this job?", coerce=int, validators=[InputRequired()])
    genre_id = SelectField("What type of music will you play?", coerce=int, validators=[InputRequired()])

class AddRegion(FlaskForm):
    city = StringField("City", validators=[InputRequired()])
    county = StringField("County", validators=[InputRequired()])
    state = StringField("State", validators=[InputRequired()])