from flask_wtf import FlaskForm
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from wtforms import PasswordField, StringField, DateField, SubmitField
from wtforms.validators import DataRequired

from app import db, login_manager


class User(db.Model, UserMixin):

    """
    This class captures users on our page
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RegistrationForm(FlaskForm):
    """
    This class is for user registratiom forms
    """

    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LogInForm(FlaskForm):
    """
    The class is for log in forms
    """
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Login')


class UserBL():
    """
    The class has the business logic layer for Users credentials
    """
    def UserFromDB(username):
        user = User.query.filter_by(username=username).first()
        return user

    def EmailFromDB(email):
        user = User.query.filter_by(email=email).first()
        return user

    def RegisterUserDB(user):
        user_search = User.query.filter_by(username=user.username).first()
        email_c = User.query.filter_by(email=user.email).first()

        if user_search is None and email_c is None:
            db.session.add(user)
            db.session.commit()
            return "User registered"

        elif email_c is not None and email_c.email == user.email:
            return "Email address already taken"

        elif user_search is not None and user_search.username == user.username:
            return "Username already taken"

    def DeleteUserDB(username):
        User.query.filter(User.username == username).delete()
        db.session.commit()


db.create_all()
db.session.commit()

# This callback is used to reload the user object from the stored user ID
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
