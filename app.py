import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, session, g, send_from_directory, current_app as app
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import requests

from models import User, Instrument, Region, Genre, UserGenre, Role, UserRole, UserInstrument, UserCV, Study, JobPost, EventPost, UserPiece, connect_db, db
from forms import UserAddForm, UserInfoForm, AddCVForm, LoginForm, JobForm, EventForm, AddRegion, UserInstrumentForm, UserGenreForm, UserSearchForm, FindWorkForm, FindComposerForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.jinja_env.filters['zip'] = zip
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql:///cascade_link'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['UPLOADED_CV_DEST'] = 'uploads/cv'
#toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

cv = UploadSet('cv', ['pdf'])
configure_uploads(app, cv)

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
        jobs = JobPost.query.all()
        return render_template("home.html", users=users, events=events, jobs=jobs)
    else:
        return render_template('home-anon.html')



############################ User Routes #################################

@app.route('/users')
def list_users():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        users = User.query.all()
        return render_template("/users/user-list.html", users=users)

@app.route('/users/search', methods=["GET", "POST"])
def search_users():
    form = UserSearchForm()
    if form.validate_on_submit():
        field = form.user_attributes.data
        info = form.search_info.data
        if field == "first_name":
            users = User.query.filter(User.first_name.ilike(info)).all()
            return render_template("users/search-results.html", users=users)
        if field == "last_name":
            users = User.query.filter(User.last_name.ilike(info)).all()
            return render_template("users/search-results.html", users=users)
        if field == "email":
            users = User.query.filter(User.email.ilike(info)).all()
            return render_template("users/search-results.html", users=users)
    return render_template("users/user-search-list.html", form=form)

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

        #get list of user instruments
        genres_list = []
        if user.genres:
            genres= list(user.genres)           
            k = 0
            while k < len(genres):
                genres_list.append(genres[k].genre)
                k += 1
        events = EventPost.query.filter_by(user_id=user_id)
        #get a list of piece ids
        pieces = UserPiece.query.filter_by(user_id=user_id)
        id_list = []
        id_list_str = []
        for piece in pieces:
            id_list.append(piece.piece_id)
            id_list_str.append(f"w:{piece.piece_id}")
        id_list = str(id_list)
        pieces_resp = requests.get(f"https://api.openopus.org/work/list/ids/{id_list[1:-1]}.json")
        user_pieces = pieces_resp.json()
        return render_template('users/profile.html', user=user, events=events, id_list=id_list_str, works=user_pieces, instruments=instruments_list, roles=roles_list, genres=genres_list)
    else:
        return render_template('home-anon.html')

@app.route('/users/<int:user_id>/edit', methods=["GET","POST"])
def edit_user(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        regions = Region.query.all()

        # list of tuples for selectfield
        region_list = [(i.id, i.city) for i in regions]
        form = UserInfoForm()
        #passing selectfield choice into the form
        form.region_id.choices = region_list
       
        if form.validate_on_submit():
            user = User.query.get_or_404(user_id)
            user.image_url = form.image_url.data
            user.bio = form.bio.data
            user.website = form.website.data
            user.region_id = form.region_id.data

            db.session.add(user)
            db.session.commit()

            return redirect(f'/users/{user_id}')
        return render_template('users/user-add-info.html', form=form)

@app.route('/users/<int:user_id>/add-cv', methods=["GET","POST"])
def add_user_cv(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        form = AddCVForm()
        if form.validate_on_submit():
            filename = cv.save(form.file.data)
            cv_info = UserCV(user_id=user_id, filename=filename)
            db.session.add(cv_info)
            db.session.commit()

            return redirect(f'/users/{user_id}')
        return render_template('users/add-cv.html', form=form)

@app.route('/users/<int:user_id>/view-cv')
def view_user_cv(user_id):
    file_info = UserCV.query.filter_by(user_id=user_id).first()
    if file_info == None:
        flash("User has not Uploaded CV yet!", "warning")
        return redirect(f'/users/{user_id}')
    return send_from_directory(app.config['UPLOADED_CV_DEST'], file_info.filename, as_attachment=True)
    

@app.route('/users/<int:user_id>/add-instrument', methods=["GET","POST"])
def edit_user_instruments(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        instruments = Instrument.query.all()
        instrument_list = [(k.id, k.instrument) for k in instruments]
        form = UserInstrumentForm()
        form.instrument_id.choices = instrument_list
        if form.validate_on_submit():
            try:
                selected_instruments= form.instrument_id.data
                i = 0
                while i < len(selected_instruments):
                    user_instrument = UserInstrument(user_id=user_id, instrument_id=form.instrument_id.data[i])
                    db.session.add(user_instrument)
                    db.session.commit()
                    i+=1
                return redirect(f'/users/{user_id}')
            
            except IntegrityError:
                flash("You have already added one or more of these instruments", 'danger')
                return render_template('users/{user_id}/add-genre', form=form)
        return render_template('users/instrument-add.html', form=form)

@app.route('/users/<int:user_id>/add-genre', methods=["GET","POST"])
def edit_user_genres(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user and session[CURR_USER_KEY] == user_id:
        genres = Genre.query.all()
        genre_list = [(j.id, j.genre) for j in genres]
        form = UserGenreForm()
        form.genre_id.choices = genre_list
        if form.validate_on_submit():
            try:
                selected_genre = form.genre_id.data
                i = 0
                while i < len(selected_genre):
                    user_genre = UserGenre(user_id=user_id, genre_id=form.genre_id.data[i])
                    db.session.add(user_genre)
                    db.session.commit()
                return redirect(f'/users/{user_id}')
            except IntegrityError:
                flash("You have already added one or more of these genres", 'danger')
                return render_template('users/genre-add.html', form=form)
            
        return render_template('users/genre-add.html', form=form)
        


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
        genres = Genre.query.all()
        genre_list = [(j.id, j.genre) for j in genres]
        regions = Region.query.all()
        # list of tuples for selectfield
        region_list = [(i.id, i.city) for i in regions]
        form = EventForm()
        #passing selectfield choice into the form
        form.region_id.choices = region_list
        form.genre_id.choices = genre_list
        if form.validate_on_submit():
            event = EventPost(title=form.title.data, 
                          description=form.description.data, 
                          address=form.address.data, 
                          date=form.date.data, 
                          region_id=form.region_id.data, 
                          user_id=user_id, 
                          genre_id=form.genre_id.data)

            db.session.add(event)
            db.session.commit()
            return redirect(f"/users/{user_id}")
        return render_template("events/event-form.html", form=form)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route('/events/<int:event_id>/cancel', methods=["POST"])
def cancel_event(event_id):  
    event = EventPost.query.get_or_404(event_id)
    if not g.user or g.user.id != event.user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        event.cancelled = True
        db.session.add(event)
        db.session.commit()
        return redirect("/events")

@app.route('/events/<int:event_id>/delete', methods=["POST"])
def delete_event(event_id):  
    event = EventPost.query.get_or_404(event_id)
    if not g.user or g.user.id != event.user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        db.session.delete(event)
        db.session.commit()
        return redirect("/events")
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
        genres = Genre.query.all()
        regions = Region.query.all()
        # list of tuples for selectfield
        region_list = [(i.id, i.city) for i in regions]
        genre_list = [(j.id, j.genre) for j in genres]
        form = JobForm()
        #passing selectfield choice into the form
        form.region_id.choices = region_list
        form.genre_id.choices = genre_list
        if form.validate_on_submit():
            job = JobPost(title=form.title.data, 
                          description=form.description.data, 
                          pay=form.pay.data, 
                          date=form.date.data, 
                          region_id=form.region_id.data, 
                          user_id=user_id, 
                          genre_id=form.genre_id.data)

            db.session.add(job)
            db.session.commit()
            return redirect(f"/users/{user_id}")
        return render_template("jobs/job-form.html", form=form)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route('/jobs/<int:job_id>/fill', methods=["POST"])
def fill_job(job_id):  
    job = JobPost.query.get_or_404(job_id)
    if not g.user or g.user.id != job.user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        job.available = False
        db.session.add(job)
        db.session.commit()
        return redirect("/jobs")

@app.route('/jobs/<int:job_id>/delete', methods=["POST"])
def delete_job(job_id):  
    job = JobPost.query.get_or_404(job_id)
    if not g.user or g.user.id != job.user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        db.session.delete(job)
        db.session.commit()
        return redirect("/jobs")

######################## Song Routes ##############################
@app.route('/works/<int:piece_id>')
def work_page(piece_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        piece_info = requests.get(f"https://api.openopus.org/work/detail/{piece_id}.json")
        piece_info = piece_info.json()
        return render_template('works/work-page.html', piece_info=piece_info)

@app.route('/works/<int:piece_id>/add', methods=["POST"])
def add_user_work(piece_id):
    """Adds pieces to the user's repertoire"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        try:
            user_id = g.user.id
            user_piece = UserPiece(user_id=user_id, piece_id=piece_id)
            db.session.add(user_piece)
            db.session.commit()
            return redirect(f'/users/{user_id}')
        except IntegrityError:
                flash("You have already added this piece", 'danger')
                return redirect(f'/users/{user_id}')
        
@app.route('/works/composers/search')
def find_composer():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        return render_template('works/find-composer.html')

@app.route('/works/composers/results')
def composer_list():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        search_input = request.args["name"]
        composer_list = requests.get(f"https://api.openopus.org/composer/list/search/{search_input}.json")
        composers = composer_list.json()
        composer_names = []
        composer_ids = []
        composer_eras = []
        i = 0
        while i <len(composers["composers"]):
            composer_names.append(composers["composers"][i]["complete_name"])
            composer_ids.append(composers["composers"][i]["id"])
            composer_eras.append(composers["composers"][i]["epoch"])
            i+= 1
        return render_template('works/composer-results.html', info=zip(composer_names,composer_eras,composer_ids))

@app.route('/works/composers/<int:composer_id>', methods=["GET", "POST"])
def composer_page(composer_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        works_resp = requests.get(f"https://api.openopus.org/work/list/composer/{composer_id}/Popular.json")
        works = works_resp.json()
        return render_template('works/composer-page.html', works=works)

@app.route('/works/composers/<int:composer_id>/results')
def composer_work_search(composer_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if g.user:
        genre = request.args["genre"]
        title = request.args["title"]
        works_resp = requests.get(f"https://api.openopus.org/work/list/composer/{composer_id}/genre/{genre}/search/{title}.json")
        works = works_resp.json()
        return render_template("works/work-search-results.html", works=works)
