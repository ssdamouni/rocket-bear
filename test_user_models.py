"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///cascade_link_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        self.client = app.test_client()
        
        db.drop_all()
        db.create_all()
        
        Steve1 = User.signup(username="Steve1", password="password", first_name="steven", last_name="damouni", email="Steve1@email.com")
        Steveid1 = 1111
        Steve1.id = Steveid1
        
        Steve2 = User.signup(username="Steve2", password="password", first_name="steven", last_name="damouni", email="Steve2@email.com")
        Steveid2 = 2222
        Steve2.id = Steveid2

        Steve3 = User.signup(username="Steve3", password="password", first_name="steven", last_name="damouni", email="Steve3@email.com")
        Steveid3 = 3333
        Steve3.id = Steveid3

        db.session.commit()

        Steve1 = User.query.get(Steveid1)
        Steve2 = User.query.get(Steveid2)
        Steve3 = User.query.get(Steveid3)

        self.Steve1 = Steve1
        self.Steveid1 = Steveid1

        self.Steve2 = Steve2
        self.Steveid2 = Steveid2

        self.Steve3 = Steve3
        self.Steveid3 = Steveid3

        self.client = app.test_client()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="Chris", 
            password="password", 
            first_name="chris", 
            last_name="young", 
            email="chris@email.com"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.full_name, "chris young")
    
    def test_bad_signup(self):
        bad_signup = User.signup(username="Steve3", password="password", first_name="steven", last_name="damouni",email="wiener@gmail.com")
        db.session.add(bad_signup)
        uid = 123456789
        bad_signup.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_user_authenticate(self):
        """Does authentication work?"""
        self.assertEqual(User.authenticate("Steve3", "password"), User.query.get(3333))
        self.assertEqual(User.authenticate("Steve3", "password3"), False)
        self.assertEqual(User.authenticate("Steve5", "password"), False)
    
    def test_user_signup(self):
        """Does a good sign up raise an error?"""
        signup =  User.signup(username="user", password="password", first_name="iser", last_name="user", email="user@email.com")
        db.session.add(signup)
        uid = 4444
        signup.id = uid
        db.session.commit()