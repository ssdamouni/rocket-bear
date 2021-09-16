from app import CURR_USER_KEY, app
from flask import session
from unittest import TestCase
from models import EventPost, db, User, Region, Genre, Instrument
from datetime import datetime



app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTest(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()
        
        Steve1 = User.signup(username="Steve1", password="password", first_name="steven", last_name="damouni", email="Steve1@email.com")
        Steveid1 = 1111
        Steve1.id = Steveid1

        genre1 = Genre(genre="classical")
        genre1id = 1111
        genre1.id = genre1id

        region1 = Region(city="Seattle", county="King", state="Washington")
        region1id = 1111
        region1.id = region1id

        instrument1 = Instrument(instrument="piano")
        instrument1id = 1111
        instrument1.id = instrument1id

        db.session.add(genre1)
        db.session.add(region1)
        db.session.add(instrument1)
        db.session.commit()

        Steve1 = User.query.get(Steveid1)
        genre1 = Genre.query.get(genre1id)
        region1 = Region.query.get(region1id)
        instrument1 = Instrument.query.get(instrument1id)

        self.Steve1 = Steve1
        self.Steveid1 = Steveid1

        self.genre1 = genre1
        self.genre1id = genre1id

        self.region1 = region1
        self.region1id = region1id

        self.instrument1 = instrument1
        self.instrument1id = instrument1id

        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_home_page(self):
        with app.test_client() as client:
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h2>Welcome to rocketbear! Let's get you logged in or create a new account!</h2>", html)

    def test_redirection(self):
        with app.test_client() as client:
            res = client.get('/users')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')

    def test_user_login(self):
        """can user login"""
        with app.test_client() as client:
            d = {"username": "Steve1", "password": "password"}
            resp = client.post("/login", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Active Musicians</h3>", html)

    def test_add_event(self):
        """Can user add a event?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.Steveid1
            
            date = datetime.now()
            date_string = date.strftime('%Y-%m-%dT%H:%M')
            d = {"title": "Hello", "description":"a concert", "address":"123 main street", "date": date_string, "region_id": 1111, "genre_id": 1111}
            resp = c.post(f'/users/{self.Steveid1}/events/new', data=d)
            self.assertEqual(resp.status_code, 302)

            event = EventPost.query.one()
            self.assertEqual(event.user_id, sess[CURR_USER_KEY])
