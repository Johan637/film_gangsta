import os
from flask import Flask, render_template, request, redirect, url_for
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
    description = db.Column(db.Text)
    year = db.Column(db.Integer)
    category = db.Column(db.String(64))

    def __init__(self, title, description, director_id, year, category):
        self.title = title
        self.decription = description
        self.director_id
        self.year = year
        self.category = category


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
    email = db.Column(db.Text)
    password = db.Column(db.Text)

    def __init__(self, email, name, password):
        self.email = email
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


def get_users(name="", email=""):
    users = None
    if name:
        users = db.session.execute(db.select(User).filter_by(name=name)).scalars().all()
    elif email:
        users = db.session.execute(db.select(User).filter_by(email=email)).scalars().all()
    else:
        users = db.session.execute(db.select(User)).scalars().all()
    return users


def get_user_dict(user):
    result = {}
    if user:
        result['name'] = user.name
        result['email'] = user.email
    return result


def create_user(email, name, password):
    if get_users(name=name) or get_users(email=email):
        return
    salt = bcrypt.gensalt()
    user = User(email, name, bcrypt.hashpw(password.encode('utf8'), salt))
    db.session.add(user)
    db.session.commit()
    return user


@app.route('/')
def index():
    return render_template("index.html", login_form=False, signin_form=False, user=get_user_dict(ACTIVE_USER))


@app.route('/login_form')
def login_form():
    return render_template("index.html", login_form=True, signin_form=False, user=get_user_dict(ACTIVE_USER))


@app.route('/login', methods=["POST"])
def login():
    email = False
    username = request.form.get("username")
    if "@" in username:
        email = True
    password = request.form.get("password")
    users = None
    if email:
        users = get_users(email = username)
    else:
        users = get_users(username)
    luser = None #login user
    for user in users:
        if bcrypt.checkpw(password.encode('utf8'), user.password):
            luser = user
            break
    if luser:
        global ACTIVE_USER
        ACTIVE_USER = luser # no u
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    global ACTIVE_USER
    ACTIVE_USER = None
    return redirect(url_for('index'))


@app.route('/signin_form')
def signin_form():
    return render_template("index.html", signin_form = True, login_form=False, user=get_user_dict(ACTIVE_USER))


@app.route('/signin', methods = ["POST"])
def signin():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    global ACTIVE_USER
    ACTIVE_USER = create_user(email, username, password)
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()

