import random
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, FindMovieForm, RateMovieForm, FindTVShowForm, RateTVShowForm, \
    FindFriendForm, UpdateInfoForm, ChangePasswordForm
import glob
import os
import requests

MOVIE_API_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_API_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_API_KEY = '5ef830d39421aa3304c12231c423a05d'
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
    firstname = db.Column(db.String(1000))
    lastname = db.Column(db.String(1000))
    avatar_url = db.Column(db.String(100))
    location = db.Column(db.String(100))
    movie = relationship("Movie", back_populates="user")
    show = relationship("TVShow", back_populates="user")
    friend = relationship("Friend", back_populates="user")
    movie_wishlist = relationship("MovieWishlist", back_populates="user")
    show_wishlist = relationship("ShowWishlist", back_populates="user")


class Friend(db.Model):
    __tablename__ = "friend"
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer)
    friend_name = db.Column(db.String(1000))
    friend_avatar_url = db.Column(db.String(100))
    friend_location = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="friend")


class Avatar(db.Model):
    __tablename__ = "avatar"
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(100))


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


class MovieWishlist(db.Model):
    __tablename__ = "movie_wishlist"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    friend = db.Column(db.String(250), nullable=False)
    friend_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="movie_wishlist")


class ShowWishlist(db.Model):
    __tablename__ = "show_wishlist"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    friend = db.Column(db.String(250), nullable=False)
    friend_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="show_wishlist")


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


# db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html", logged_in=False)


@app.route('/registration', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
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
        rand_avatar = Avatar.query.filter_by(id=random.choice(range(1, 80))).first()
        new_user = User(
            email=form.email.data,
            firstname=form.firstname.data.title(),
            lastname=form.lastname.data.title(),
            location=form.location.data.title(),
            password=hash_and_salted_password,
            avatar_url=rand_avatar.img_url
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user_home', user=current_user.id))
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
            return redirect(url_for('user_home', user=current_user.id))
    return render_template("login.html", form=form, logged_in=False)


@app.route("/user")
@login_required
def user_home():
    name = current_user.firstname
    user = User.query.get(current_user.id)
    users_with_pic = user.avatar_url
    if users_with_pic:
        my_avatar = str(user.avatar_url)
        db.session.commit()
    else:
        my_avatar = "./static/img/avatars/avatar_24.png"
    return render_template("user_home.html", current_user=current_user, name=name, logged_in=True,
                           profile_image=my_avatar, user=current_user.id)


path = "./static/img/avatars/*.png"
files = glob.glob(path)


def add_pics_to_db():
    for image in files:
        new_avatar = Avatar(
            img_url=image,
        )
        db.session.add(new_avatar)
        db.session.commit()


@app.route("/pics", methods=["GET", "POST"])
@login_required
def change_pic():
    avatar_pics = Avatar.query.all()
    return render_template("change_pic.html", pictures=avatar_pics, logged_in=True)


@app.route("/user/<int:pic_id>")
@login_required
def select_pic(pic_id):
    avatar = Avatar.query.filter_by(id=pic_id).first()
    user = User.query.get(current_user.id)
    friend_pics = Friend.query.filter_by(friend_id=current_user.id).all()
    avatar_select = avatar.img_url
    user.avatar_url = avatar_select
    for item in friend_pics:
        item.friend_avatar_url = avatar_select
    db.session.commit()
    return redirect(url_for('user_home'))


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


@app.route("/friends")
@login_required
def friends():
    all_friends = Friend.query.filter(Friend.user_id == current_user.id).all()
    return render_template("friends.html", friends=all_friends, logged_in=True, current_user=current_user)


@app.route("/search_for_friend", methods=["GET", "POST"])
@login_required
def search_friend():
    all_users = User.query.filter(User.id != current_user.id).order_by(User.lastname).all()
    form = FindFriendForm()
    no_results = False
    if form.validate_on_submit():
        search = form.name.data
        name = search.title()
        results = []
        for user in all_users:
            first_name = user.firstname
            lat_name = user.lastname
            full_name = f"{user.firstname} {user.lastname}"
            if name == first_name or name == lat_name or name == full_name:
                results.append(user)
        db.session.commit()
        if len(results) == 0:
            no_results = True
        return render_template("search_one_friend.html", results=results, logged_in=True, no_results=no_results)
    db.session.commit()
    return render_template('search_friends.html', users=all_users, logged_in=True, current_user=current_user, form=form)


@app.route('/<int:selected_user>', methods=["GET", "POST"])
@login_required
def user_profile(selected_user):
    already_added = False
    this_user = User.query.get(selected_user)
    first_name = this_user.firstname
    last_name = this_user.lastname
    full_name = f"{first_name} {last_name}"
    added = Friend.query.filter((Friend.user_id == current_user.id), (Friend.friend_id == this_user.id)).all()
    if len(added) != 0:
        already_added = True
    avatar_url = this_user.avatar_url
    db.session.commit()
    return render_template("user_profile.html", logged_in=True, name=full_name, user=this_user,
                           profile_image=avatar_url, added=already_added, first_name=first_name)


@app.route("/friend_movies/<int:selected_user>")
@login_required
def friend_movies(selected_user):
    this_user = User.query.get(selected_user)
    first_name = this_user.firstname
    all_movies = Movie.query.filter(Movie.user_id == selected_user).order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("friend_movies.html", movies=all_movies, logged_in=True, user=this_user,
                           name=first_name)


@app.route("/friend_shows/<int:selected_user>")
@login_required
def friend_shows(selected_user):
    this_user = User.query.get(selected_user)
    first_name = this_user.firstname
    all_shows = TVShow.query.filter(TVShow.user_id == selected_user).order_by(TVShow.rating).all()
    for i in range(len(all_shows)):
        all_shows[i].ranking = len(all_shows) - i
    db.session.commit()
    return render_template("friend_shows.html", shows=all_shows, logged_in=True, user=this_user,
                           name=first_name)


@app.route('/friends/<int:selected_user>')
@login_required
def add_to_my_friends(selected_user):
    friend = User.query.get(selected_user)
    friend_id = friend.id
    friend_avatar = friend.avatar_url
    first_name = friend.firstname
    last_name = friend.lastname
    friend_location = friend.location
    friend_name = f"{first_name} {last_name}"
    new_friend = Friend(
        user=current_user,
        friend_id=friend_id,
        friend_name=friend_name,
        friend_avatar_url=friend_avatar,
        friend_location=friend_location
    )
    db.session.add(new_friend)
    db.session.commit()
    return redirect(url_for('friends'))


@app.route('/friend/<int:selected_user>')
@login_required
def remove_friend(selected_user):
    this_user = User.query.get(selected_user)
    friendship = Friend.query.filter((Friend.user_id == current_user.id), (Friend.friend_id == this_user.id)).all()
    for item in friendship:
        friend_id = item.id
        remove = Friend.query.get(friend_id)
        db.session.delete(remove)
        db.session.commit()

    return redirect(url_for("friends"))


@app.route("/wishlist")
@login_required
def wishlist():
    shows_w = ShowWishlist.query.filter(ShowWishlist.user_id == current_user.id).order_by(ShowWishlist.title).all()
    movies_w = MovieWishlist.query.filter(MovieWishlist.user_id == current_user.id).order_by(MovieWishlist.title).all()
    db.session.commit()
    return render_template("wishlist.html", shows=shows_w, movies=movies_w, logged_in=True, current_user=current_user)


@app.route("/movie_wishlist/<int:movie_id>/<int:friend_id>")
@login_required
def movie_wishlist(movie_id, friend_id):
    movie = Movie.query.get(movie_id)
    movie_review = movie.review
    if movie.review is None:
        movie_review = "No Review"
    friend = User.query.get(friend_id)
    friend_name = f"{friend.firstname} {friend.lastname}"
    friend_id = friend.id
    new_movie_wishlist = MovieWishlist(
        title=movie.title,
        year=movie.year,
        img_url=movie.img_url,
        description=movie_review,
        friend=friend_name,
        friend_id=friend_id,
        user=current_user
    )
    db.session.add(new_movie_wishlist)
    db.session.commit()
    return redirect(url_for("wishlist", friend=friend))


@app.route("/show_wishlist/<int:show_id>/<int:friend_id>")
@login_required
def show_wishlist(show_id, friend_id):
    show = TVShow.query.get(show_id)
    show_review = show.review
    if show.review is None:
        show_review = "No Review"
    friend = User.query.get(friend_id)
    friend_name = f"{friend.firstname} {friend.lastname}"
    friend_id = friend.id
    new_show_wishlist = ShowWishlist(
        title=show.title,
        year=show.year,
        img_url=show.img_url,
        description=show_review,
        friend=friend_name,
        friend_id=friend_id,
        user=current_user
    )
    db.session.add(new_show_wishlist)
    db.session.commit()
    return redirect(url_for("wishlist", friend=friend))


@app.route("/show_wishlist/<int:show_id>")
@login_required
def show_wishlist_remove(show_id):
    show = ShowWishlist.query.get(show_id)
    db.session.delete(show)
    db.session.commit()
    return redirect(url_for("wishlist"))


@app.route("/movie_wishlist/<int:movie_id>")
@login_required
def movie_wishlist_remove(movie_id):
    movie = MovieWishlist.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("wishlist"))


@app.route("/add_movie", methods=["GET", "POST"])
@login_required
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_API_SEARCH_URL, params={"api_key": MOVIE_API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select_movie.html", options=data, movie_img=MOVIE_IMG_URL, logged_in=True,
                               current_user=current_user)
    return render_template("add_movie.html", form=form, logged_in=True, current_user=current_user)


@app.route("/add_show", methods=["GET", "POST"])
@login_required
def add_show():
    form = FindTVShowForm()
    if form.validate_on_submit():
        show_title = form.title.data
        response = requests.get(TV_API_SEARCH_URL, params={"api_key": MOVIE_API_KEY, "query": show_title})
        data = response.json()["results"]
        return render_template("select_show.html", options=data, logged_in=True, show_img=TV_IMG_URL,
                               current_user=current_user)
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


@app.route("/edit_movies", methods=["GET", "POST"])
@login_required
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if request.method == "POST" and form.validate():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('movies'))
    return render_template("edit_movie.html", movie=movie, form=form, current_user=current_user, logged_in=True)


@app.route("/edit_show", methods=["GET", "POST"])
@login_required
def rate_show():
    form = RateTVShowForm()
    show_id = request.args.get("id")
    show = TVShow.query.get(show_id)
    if request.method == "POST" and form.validate():
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


@app.route('/update_info', methods=["GET", "POST"])
@login_required
def update_info():
    form = UpdateInfoForm()
    user = User.query.get(current_user.id)
    first_name = user.firstname
    last_name = user.lastname
    full_name = f"{first_name} {last_name}"
    as_friends = Friend.query.filter_by(friend_id=current_user.id).all()
    if request.method == "POST" and form.validate():
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.location = form.location.data
        for item in as_friends:
            item.friend_name = full_name
            item.friend_location = user.location
        db.session.commit()
        return redirect(url_for('user_home'))
    return render_template("update_info.html", form=form, logged_in=True, current_user=current_user)


@app.route('/update_password', methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    user = User.query.get(current_user.id)

    if request.method == "POST" and form.validate():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        user.password = hash_and_salted_password
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("change_password.html", form=form, logged_in=True, current_user=current_user)


@app.route('/are_you_sure')
@login_required
def are_you_sure():
    return render_template("are_you_sure.html")


@app.route('/delete_account')
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    as_friends = Friend.query.filter_by(friend_id=current_user.id).all()
    as_movies = Movie.query.filter_by(user_id=current_user.id).all()
    as_shows = TVShow.query.filter_by(user_id=current_user.id).all()

    for item in as_friends:
        db.session.delete(item)
    for item in as_movies:
        db.session.delete(item)
    for item in as_shows:
        db.session.delete(item)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template("about.html")

# add_pics_to_db()


if __name__ == '__main__':
    app.run(debug=True)
