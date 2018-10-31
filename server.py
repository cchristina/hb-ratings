"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from datetime import datetime, timedelta 

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():

    users = User.query.all()
    return render_template("user_list.html", users=users)



@app.route('/movies')
def movie_list():

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies) 


@app.route('/register', methods=["GET", "POST"])
def register():
    if (request.method=="GET"):
        return render_template("register_form.html")

    elif (request.method=="POST"):

        email = request.form.get("reg-email")
        pw = request.form.get("pw") #this doesn't feel very secure
        dob = request.form.get("dob") #yyyy-mm-dd 
        zipcode = request.form.get("zipcode")

        dobdt = datetime.strptime(dob, "%Y-%m-%d")
        now = datetime.now()
        age = int((now - dobdt).days/365)
        #print(age, type(age), "************************************")

        if (not User.query.filter_by(email=email).first()):
            
            print(type(dobdt), dobdt)
            new_user = User(email=email, password=pw, age=age, zipcode=zipcode)
            db.session.add(new_user)
            db.session.commit()

            return redirect("/")

        else:
            return redirect("/login")
            #you already have an account flash

        return redirect("/")


@app.route('/login', methods=["GET", "POST"])
def login():
    if  (request.method=="GET"): #log in form


        if (session.get("current_user", 0)): #checks if user is logged in this is ugly and not the way to do it please fix
            return redirect ("/logout")

        else:
            return render_template("login.html")

    


    else: 
        #processing login form
        email = request.form.get("log-email")
        pw = request.form.get("password") #this still doesn't feel very secure

        try: #tries to query the login information
            current_user = User.query.filter_by(email=email).first()
            queryPW= current_user.password

        except: #email is not valid redirects user to register an account
            flash("You do not yet have an account, please register!")
            return redirect("/register") #add flash message telling to register
      
        
        if (pw==queryPW): #checks if password is accurate

            session['current_user']=current_user.user_id
            flash("You have logged in!")

            return redirect ("/")
        
        else:
            flash('wrong password')
            return redirect("/login")

     #    945 | test@example.com     | 1234     |  36 | 94509
     #    946 | testuser@example.com | passw0rd |  35 | 12345


@app.route("/logout", methods=["GET", "POST"])
def handle_logout():

    if (request.method=="GET"):
        return render_template("logout.html")

    else:
        if request.form.get("logout"):
            session['current_user'] = None
            flash("you have logged out")
            return redirect("/")
        else:
            flash("you are still logged in")
            return redirect("/")


@app.route('/users/<user_id>', methods=["GET"])
def render_lookup(user_id):

    user = User.query.filter_by(user_id = user_id).first()
    email = user.email
    age = user.age
    zipcode = user.zipcode

    if (email==None):
        email = "no email supplied"
    

    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    movie_ratings = {}

    for rating in user_ratings:
        movie_title = Movie.query.filter_by(movie_id = rating.movie_id).first().title
        movie_ratings[movie_title] = rating.score


    return render_template("userlookup.html", user_id = user_id, email=email, age=age, zipcode=zipcode, movie_ratings = movie_ratings)

@app.route('/movie/<movie_id>', methods=["GET"])
def render_movie_lookup(movie_id):

    movie = Movie.query.filter_by(movie_id = movie_id).first()
    movie_ratings = Rating.query.filter_by(movie_id = movie_id).all()
    user_ratings = {}

    #user id, grab from list of all ratings
    # rating, also grab from list of all ratings 
    for rating in movie_ratings:
        user_ratings[rating.user_id] = rating.score
   

    movie_title = movie.title
    release = str(movie.released_at) #fix this to more proper version later
    imdb = movie.imdb_url
    #movie_id
    #title
    #relased_at (year)
    #imdb_url 

    return render_template("movielookup.html", movie_title = movie_title, release = release, imdb=imdb)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
