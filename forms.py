from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators


class RegistrationForm(FlaskForm):
    firstname = StringField("First Name", [validators.DataRequired()])
    lastname = StringField("Surname", [validators.DataRequired()])
    location = StringField("City / Town", [validators.DataRequired()])
    email = StringField("Email", [validators.DataRequired(),
                                  validators.Email(), validators.Length(min=6, max=35)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Sign Me Up!")


class UpdateInfoForm(FlaskForm):
    firstname = StringField("First Name", [validators.DataRequired()])
    lastname = StringField("Surname", [validators.DataRequired()])
    location = StringField("City / Town", [validators.DataRequired()])
    submit = SubmitField("Update Info!")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("New Password", [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat New Password')
    submit = SubmitField("Change!")


class LoginForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])
    submit = SubmitField("Let Me In!")


class FindMovieForm(FlaskForm):
    title = StringField(" ", [validators.DataRequired()])
    submit = SubmitField("Search Movie")


class RateMovieForm(FlaskForm):
    rating = StringField("Rating Out of 10 e.g. 7.5", [validators.DataRequired()])
    review = StringField("Write A Short Review")
    submit = SubmitField("Done")


class FindTVShowForm(FlaskForm):
    title = StringField(" ", [validators.DataRequired()])
    submit = SubmitField("Search Show")


class RateTVShowForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", [validators.DataRequired()])
    review = StringField("Write A Short Review")
    submit = SubmitField("Done")


class FindFriendForm(FlaskForm):
    name = StringField(" ", [validators.Length(min=2, max=25)])
    submit = SubmitField("Search")
