import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import User, Instrument, Region, Genre, Role, UserRole, UserInstrument, Study, JobPost, EventPost, connect_db, db
from forms import UserAddForm, LoginForm, JobForm, EventForm, AddRegion

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql:///cascade_link'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
#toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

############  Handle all sign up and authentication for website  ############################

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data or None,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out!", "success")
    return redirect('/')

################### Home Route ######################################

@app.route('/')
def homepage():
    """Populate homepage"""
    if g.user:
        users = User.query.all()
        events = EventPost.query.all()
        return render_template("home.html", users=users, events=events)
    else:
        return render_template('home-anon.html')



############################ User Routes #################################

@app.route('/users/<int:user_id>')
def user_profile(user_id):
    if g.user:
        user = User.query.get_or_404(user_id)
        #get list of user instruments
        instruments_list = []
        if user.instruments:
            instruments= list(user.instruments)           
            i = 0
            while i < len(instruments):
                instruments_list.append(instruments[i].instrument)
                i += 1
        
        #get list of roles
        roles_list = []
        if user.roles:
            roles= list(user.roles)
            j = 0
            while j < len(roles):
                roles_list.append(roles[j].role)
                j += 1

        events = EventPost.query.filter_by(user_id=user_id)
        return render_template('users/profile.html', user=user, events=events, instruments=instruments_list, roles=roles_list)
    else:
        return render_template('home-anon.html')

@app.route('/users/<int:user_id>/edit', methods=["POST"])
def edit_user(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        form = UserInfoForm()

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        do_logout()
        db.session.delete(g.user)
        db.session.commit()
        return redirect('/signup')

######################## Region Routes ##############################

@app.route('/regions/add', methods=["GET", "POST"])
def add_region():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        form = AddRegion()
        if form.validate_on_submit():
            region = Region(city=form.city.data, county=form.county.data, state=form.state.data)
            db.session.add(region)
            db.session.commit()
            return redirect('/')
        return render_template("region-form.html", form=form)

    
######################## Event Routes ##############################
@app.route('/events')
def list_events():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        events = EventPost.query.all()
        return render_template("/events/event-list.html", events=events)

@app.route('/events/<int:event_id>')
def specific_event(event_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        event = EventPost.query.get_or_404(event_id)
        return render_template("/events/event-page.html", event=event)

@app.route('/users/<int:user_id>/events/new', methods=["GET", "POST"])
def create_event(user_id):
    """Used by users to create job posts"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        regions = Region.query.all()
        # list of tuples for selectfield
        region_list = [(i.id, i.city) for i in regions]
        form = EventForm()
        #passing selectfield choice into the form
        form.region_id.choices = region_list
        if form.validate_on_submit():
            event = EventPost(title=form.title.data, 
                          description=form.description.data, 
                          addres=form.address.data, 
                          date=form.date.data, 
                          region_id=form.region_id.data, 
                          user_id=user_id, 
                          genre=form.genre.data)

            db.session.add(event)
            db.session.commit()
            return redirect(f"/users/{user_id}")
        return render_template("events/event-form.html", form=form)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


######################## Job Routes ##############################
@app.route('/jobs')
def list_jobs():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        jobs = JobPost.query.all()
        return render_template("/jobs/job-list.html", jobs=jobs)

@app.route('/jobs/<int:job_id>')
def specific_job(job_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        job = JobPost.query.get_or_404(job_id)
        return render_template("/jobs/job-page.html", job=job)


@app.route('/users/<int:user_id>/jobs/new', methods=["GET", "POST"])
def create_job(user_id):
    """Used by users to create job posts"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        regions = Region.query.all()
        # list of tuples for selectfield
        region_list = [(i.id, i.city) for i in regions]
        form = JobForm()
        #passing selectfield choice into the form
        form.region_id.choices = region_list
        if form.validate_on_submit():
            job = JobPost(title=form.title.data, 
                          description=form.description.data, 
                          pay=form.pay.data, 
                          date=form.date.data, 
                          region_id=form.region_id.data, 
                          user_id=user_id, 
                          genre=form.genre.data)

            db.session.add(job)
            db.session.commit()
            return redirect(f"/users/{user_id}")
        return render_template("/job-form.html", form=form)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


