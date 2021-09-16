from app import app
from flask import session
from unittest import TestCase
from models import db, User



app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

class UserViewTest(TestCase):
    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()
        
        Steve1 = User.signup(username="Steve1", password="password", first_name="steven", last_name="damouni", email="Steve1@email.com")
        Steveid1 = 1111
        Steve1.id = Steveid1

        db.session.commit()

        Steve1 = User.query.get(Steveid1)

        self.Steve1 = Steve1
        self.Steveid1 = Steveid1

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
        with app.test_client() as client:
            d = {"username": "Steve1", "password": "password"}
            resp = client.post("/login", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h3 class='h2 mt-3'>Active Musicians</h3>", html)
