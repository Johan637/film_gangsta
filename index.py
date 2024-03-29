import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt


app = Flask(__name__)

# Sleutel opgeven voor het gebruik van Forms
app.config['SECRET_KEY'] = 'mysecretkey'
IMG_FOLDER = os.path.join('static', 'thumbnails')
app.config["UPLOAD_FOLDER"] = IMG_FOLDER

# DATABASE en MODELS

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
ACTIVE_USER = None
CENTRAL_DICT = {}


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(128))

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __init__(self, name):
        self.name = name


class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    director_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    year = db.Column(db.Integer)
    thumbnail = db.Column(db.String(128))

    def __init__(self, title, description, director_id, year, category, thumbnail):
        self.title = title
        self.decription = description
        self.director_id
        self.year = year
        self.category = category
        self.thumbnail = thumbnail


class Film_Category(db.Model):
    __tablename__ = 'film_category'
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)

    def __init__(self, film_id, category_id):
        self.film_id = film_id
        self.category_id = category_id


class Actor(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    thumbnail = db.Column(db.String(128))

    def __init__(self, firstname, lastname, thumbnail):
        self.firstname = firstname
        self.lastname = lastname
        self.thumbnail = thumbnail


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer)
    film_id = db.Column(db.Integer)
    character = db.Column(db.String(64))

    def __init__(self, actor_id, film_id, character):
        self.actor_id = actor_id
        self.film_id = film_id
        self.character = character


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password


class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    character = db.Column(db.String(64))
    film_id = db.Column(db.Integer)

    def __init__(self, user_id, description, character, film_id):
        self.user_id = user_id
        self.description = description
        self.character = character
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



def get_movies(title=''):
    movies  = []
    if title:
        movies = Film.query.filter(Film.title.contains(title)).all()
    else:
        movies = db.session.execute(db.select(Film)).scalars().all()
    return movies


def get_actors(name=''):
    actors = []
    if name:
        actors.extend(db.session.execute(db.select(Actor).filter_by(firstname=name)).scalars().all())
        actors.extend(db.session.execute(db.select(Actor).filter_by(lastname=name)).scalars().all())
    else:
        actors = db.session.execute(db.select(Actor)).scalars().all()
    return actors


def get_categories(**kwargs):
    categories = db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    return categories


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


def build_dict(dict, **kwargs):
    for kw, arg in kwargs.items():
        dict[kw] = arg


@app.route('/')
def index():
    build_dict(CENTRAL_DICT, page=url_for('index'))
    return render_template("index.html", resources=CENTRAL_DICT)


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
    build_dict(CENTRAL_DICT, user=ACTIVE_USER)
    return redirect(CENTRAL_DICT['page'])


@app.route('/logout')
def logout():
    global ACTIVE_USER
    ACTIVE_USER = {}
    build_dict(CENTRAL_DICT, user=ACTIVE_USER)
    return redirect(CENTRAL_DICT['page'])


@app.route('/signin', methods=["POST"])
def signin():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    create_user(email, username, password)
    users = get_users(username)
    luser = None #login user
    for user in users:
        if bcrypt.checkpw(password.encode('utf8'), user.password):
            luser = user
            break
    if luser:
        global ACTIVE_USER
        ACTIVE_USER = luser # no u
    build_dict(CENTRAL_DICT, user=ACTIVE_USER)
    return redirect(CENTRAL_DICT['page'])


@app.route('/categories')
def categories():
    categories = {}
    if not CENTRAL_DICT.get('categories', {}):
        categories = get_categories()
    build_dict(CENTRAL_DICT, categories=categories)
    return redirect(CENTRAL_DICT['page'])


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('search')
    result = {'movies': [], 'actors': []}
    result['movies'] = get_movies(query)
    result['actors'] = get_actors(query)
    print(result['actors'])
    build_dict(CENTRAL_DICT, page='search', search=result)
    return render_template('search.html', resources=CENTRAL_DICT)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()

