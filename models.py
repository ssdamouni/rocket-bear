from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Instrument(db.Model):
    """Used to find instruments and add if needed"""

    __tablename__= 'instruments'

    id = db.Column(
        db.Integer,
        primary_key=True, unique=True
    )

    instrument = db.Column(db.Text, nullable=False)

    
    instruments = db.relationship('User', secondary="user_instruments", backref="instruments")

class UserInstrument(db.Model):
    """Keeps track of which instrument(s) each user plays"""

    __tablename__ ="user_instruments"

    user_id = db.Column(db.Integer,
                       db.ForeignKey("users.id"),
                       primary_key=True)
    instrument_id = db.Column(db.Integer,
                          db.ForeignKey("instruments.id"),
                          primary_key=True)

class Genre(db.Model):
    """Used to find musical genre and add if needed"""

    __tablename__= 'genres'

    id = db.Column(
        db.Integer,
        primary_key=True, unique=True,
    )

    genre = db.Column(db.Text, nullable=False)

class Study(db.Model):
    """Used to find instruments and add if needed"""

    __tablename__= 'Education'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    degree = db.Column(db.Text, nullable=False)

class Role(db.Model):
    """Used to describe what the user is using the site for"""

    __tablename__= 'roles'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    role = db.Column(db.Text, nullable=False, unique=True)

    roles = db.relationship('User', secondary="user_roles", backref="roles")

class UserRole(db.Model):
    """Junction table for users and roles"""
    __tablename__='user_roles'

    user_id = db.Column(db.Integer,
                       db.ForeignKey("users.id"),
                       primary_key=True)
    role_id = db.Column(db.Integer,
                          db.ForeignKey("roles.id"),
                          primary_key=True)

class Region(db.Model):
    """Used to find instruments and add if needed"""

    __tablename__= 'regions'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    city = db.Column(db.Text, nullable=False)
    county = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)

    users = db.relationship("User")

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,)

    email = db.Column(db.Text, nullable=False,unique=True,)

    username = db.Column(db.Text, nullable=False, unique=True,)
    password = db.Column(db.Text,nullable=False,)

    image_url = db.Column(db.Text,default="/static/images/default-pic.png",)
    bio = db.Column( db.Text, default="Bio will show up here!")
    website = db.Column(db.Text, default="")

    first_name = db.Column(db.Text,nullable=False,)
    last_name = db.Column(db.Text, nullable=True,)

    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), default=1)
    regions = db.relationship('Region')
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, first_name, last_name, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    
    @property
    def full_name(self):
        """Return full name of user."""
        if self.last_name==None:
            return f"{self.first_name}"
        else:
            return f"{self.first_name} {self.last_name}"


class JobPost(db.Model):
    """The way that users can find and post job oppurtunities"""

    __tablename__="job_posts"

    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    pay = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    genre = db.Column(db.Text)

    regions = db.relationship('Region')
    

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.date.strftime("%A, %D %H:%M")


class EventPost(db.Model):
    """The way that users can find and post job oppurtunities"""

    __tablename__="event_posts"

    id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    genre = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
        
    regions = db.relationship('Region')
    

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.date.strftime("%A, %D %H:%M")

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)