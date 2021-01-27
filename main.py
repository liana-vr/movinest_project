
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
import os
import requests


MOVIE_API_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_API_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_API_KEY = os.environ.get('MOVIE_API_KEY')
MOVIE_IMG_URL = "https://image.tmdb.org/t/p/w500"

TV_API_INFO_URL = "https://api.themoviedb.org/3/tv"
TV_API_SEARCH_URL = "https://api.themoviedb.org/3/search/tv"
TV_IMG_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    avatar = relationship("Avatar", back_populates="user")
    movie = relationship("Movie", back_populates="user")
    show = relationship("TVShow", back_populates="user")


class Avatar(db.Model):
    __tablename__ = "avatar"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="avatar")


class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="movie")


class TVShow(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="show")


db.create_all()


class FindMovieForm(FlaskForm):
    title = StringField("Search The Database For Movie Titles", validators=[DataRequired()])
    submit = SubmitField("Search Movie")


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Write A Short Review")
    submit = SubmitField("Done")


class FindTVShowForm(FlaskForm):
    title = StringField("Search The Database For Show Titles", validators=[DataRequired()])
    submit = SubmitField("Search Show")


class RateTVShowForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Write A Short Review")
    submit = SubmitField("Done")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html", logged_in=False)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        name = str(new_user.name).split()
        return render_template("user_home.html", name=name[0], logged_in=True)
    return render_template("register.html", form=form, current_user=current_user, logged_in=False)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            name = str(user.name).split()
            return render_template("user_home.html", name=name[0], logged_in=True)
    return render_template("login.html", form=form, logged_in=False)


@app.route("/user")
@login_required
def user_home():
    name = str(current_user.name).split()
    return render_template("user_home.html", current_user=current_user, name=name[0], logged_in=True)


@app.route("/movies")
@login_required
def movies():
    all_movies = Movie.query.filter(Movie.user_id == current_user.id).order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("movies.html", movies=all_movies, logged_in=True, current_user=current_user)


@app.route("/shows")
@login_required
def shows():
    all_shows = TVShow.query.filter(TVShow.user_id == current_user.id).order_by(TVShow.rating).all()
    for i in range(len(all_shows)):
        all_shows[i].ranking = len(all_shows) - i
    db.session.commit()
    return render_template("shows.html", shows=all_shows, logged_in=True, current_user=current_user)


@app.route("/add_movie", methods=["GET", "POST"])
@login_required
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_API_SEARCH_URL, params={"api_key": MOVIE_API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select_movie.html", options=data, logged_in=True, current_user=current_user)
    return render_template("add_movie.html", form=form, logged_in=True, current_user=current_user)


@app.route("/add_show", methods=["GET", "POST"])
@login_required
def add_show():
    form = FindTVShowForm()
    if form.validate_on_submit():
        show_title = form.title.data
        response = requests.get(TV_API_SEARCH_URL, params={"api_key": MOVIE_API_KEY, "query": show_title})
        data = response.json()["results"]
        return render_template("select_show.html", options=data, logged_in=True, current_user=current_user)
    return render_template("add_show.html", form=form, logged_in=True, current_user=current_user)


@app.route("/find_movie", methods=["GET", "POST"])
@login_required
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_API_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_IMG_URL}{data['poster_path']}",
            description=data["overview"],
            user=current_user
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie", id=new_movie.id))


@app.route("/find_show", methods=["GET", "POST"])
@login_required
def find_show():
    show_api_id = request.args.get("id")
    if show_api_id:
        show_api_url = f"{TV_API_INFO_URL}/{show_api_id}"
        response = requests.get(show_api_url, params={"api_key": MOVIE_API_KEY, "language": "en-US"})
        data = response.json()
        new_show = TVShow(
            title=data["name"],
            year=data["first_air_date"],
            img_url=f"{TV_IMG_URL}{data['poster_path']}",
            description=data["overview"],
            user=current_user
        )
        db.session.add(new_show)
        db.session.commit()
        return redirect(url_for("rate_show", id=new_show.id))


@app.route("/edit_movie", methods=["GET", "POST"])
@login_required
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('movies'))
    return render_template("edit_movie.html", movie=movie, form=form, logged_in=True, current_user=current_user)


@app.route("/edit_show", methods=["GET", "POST"])
@login_required
def rate_show():
    form = RateTVShowForm()
    show_id = request.args.get("id")
    show = TVShow.query.get(show_id)
    if form.validate_on_submit():
        show.rating = float(form.rating.data)
        show.review = form.review.data
        db.session.commit()
        return redirect(url_for('shows'))
    return render_template("edit_show.html", show=show, form=form, logged_in=True, current_user=current_user)


@app.route("/delete_movie")
@login_required
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("movies"))


@app.route("/delete_show")
@login_required
def delete_show():
    show_id = request.args.get("id")
    show = TVShow.query.get(show_id)
    db.session.delete(show)
    db.session.commit()
    return redirect(url_for("shows"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)


