from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField
from wtforms.validators import InputRequired
from wtforms.widgets import TextArea

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

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class EventForm(FlaskForm):
    title = StringField("What is the event called", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    address = StringField("What is the Address of the event?", validators=[InputRequired()])
    date = DateTimeField("Date of Event", validators=[InputRequired()])
    genre = StringField("What type of music will you play?", validators=[InputRequired()])
# class FeedbackForm(FlaskForm):
#     title = StringField("Title", validators=[InputRequired()])
#     content = StringField("Content", validators=[InputRequired()])