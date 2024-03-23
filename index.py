import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt


app = Flask(__name__)

# Sleutel opgeven voor het gebruik van Forms
app.config['SECRET_KEY'] = 'mysecretkey'

# DATABASE en MODELS

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
ACTIVE_USER = None


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname 


class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    director_id = db.Column(db.Integer)
    year = db.Column(db.Integer)

    def __init__(self, title, director_id, year):
        self.title = title
        self.director_id
        self.year = year


class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer)
    film_id = db.Column(db.Integer)
    character = db.Column(db.Text)

    def __init__(self, actor_id, film_id, character):
        self.actor_id = actor_id
        self.film_id = film_id
        self.character = character


class User(db.Model):
    # use me mommy
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)

    def __init__(self, name, password):
        self.name = name
        self.password = password


class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    film_id = db.Column(db.Integer)

    def __init__(self, user_id, description, film_id):
        self.user_id = user_id
        self.description = description
        self.film_id = film_id


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    film_id = db.Column(db.Integer)

    def __init__(self, user_id, description, film_id):
        self.user_id = user_id
        self.description = description
        self.film_id = film_id

    


def get_actors(**kwargs):
    actors = db.session.execute(db.select(Actor)).scalars()
    return actors
    


def create_actor():
    actor = Actor("Ryan", "Gosling")
    db.session.add(actor)
    db.session.commit()
    return actor 


def get_users(name = ""):
    users = None
    if name:
        users = db.session.execute(db.select(User).filter_by(name=name)).scalars()
    else:
        users = db.session.execute(db.select(User)).scalars()
    return users


def create_user(name, password):
    salt = bcrypt.gensalt()
    user = User(name, bcrypt.hashpw(password, salt))
    db.session.add(user)
    db.session.commit()
    return user 


@app.route('/')
def index():
    return render_template("index.html", login_form = None, signin_form = None)
    

@app.route('/login_form')
def login_form():
    return render_template("index.html", login_form = "block", signin_form = None)


@app.route('/login', methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    users = get_users(username)
    luser = None #login user
    for user in users:
        if bcrypt.checkpw(password, user.password):
            luser = user
            break
    if luser:
        ACTIVE_USER = luser # no u 


@app.route('/signin_form')
def signin_form():
    return render_template("index.html", signin_form = "block", login_form = None)
        

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()

