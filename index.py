import os
from flask import Flask, render_template, request, redirect, url_for, session
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


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(128))

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname

    def get(self):
        return {'id': self.id, 'firstname': self.firstname, 'lastname': self.lastname}


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __init__(self, name):
        self.name = name

    def get(self):
        return {'id': self.id, 'name': self.name}


class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'))
    description = db.Column(db.Text)
    year = db.Column(db.Integer)
    thumbnail = db.Column(db.String(128))

    def __init__(self, title, description, director_id, year, thumbnail):
        self.title = title
        self.decription = description
        self.director_id
        self.year = year
        self.thumbnail = thumbnail

    def get(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'director_id': self.director_id, 'year': self.year, 'thumbnail': self.thumbnail}


class Film_Category(db.Model):
    __tablename__ = 'film_category'
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, film_id, category_id):
        self.film_id = film_id
        self.category_id = category_id

    def get(self):
        return {'id': self.id, 'film_id': film_id, 'category_id': category_id}


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

    def get(self):
        return {'id': self.id, 'firstname': self.firstname, 'lastname': self.lastname, 'thumbnail': self.thumbnail}


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.id'))
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'))
    character = db.Column(db.String(64))

    def __init__(self, actor_id, film_id, character):
        self.actor_id = actor_id
        self.film_id = film_id
        self.character = character

    def get(self):
        return {'id': self.id, 'actor_id': self.actor_id, 'film_id': self.film_id, 'character': self.character}


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

    def get(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}


class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    character = db.Column(db.String(64))
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'))

    def __init__(self, user_id, description, character, film_id):
        self.user_id = user_id
        self.description = description
        self.character = character
        self.film_id = film_id

    def get(self):
        return {'id': self.id, 'user_id': self.user_id, 'description': self.description, 'character': self.character, 'film_id': self.film_id}




class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'))

    def __init__(self, user_id, description, film_id):
        self.user_id = user_id
        self.description = description
        self.film_id = film_id

    def get(self):
        return {'id': self.id, 'user_id': self.user_id, 'description': self.description, 'film_id': self.film_id}



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


def get_categories():
    categories = db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    return categories


def get_category(id):
    category = db.session.execute(db.select(Category).filter_by(id=id)).scalars().first()
    return category


def get_movies_by_category(id):
    movies = [mov[1] for mov in db.session.query(Film_Category, Film).filter_by(category_id=id).join(Film).all()]
    return movies



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
    build_dict(session, page=url_for('index'), categories=[cat.get() for cat in get_categories()], search='')
    return render_template("index.html", resources=session)


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
    build_dict(session, user=luser.get())
    return redirect(session['page'])


@app.route('/logout')
def logout():
    build_dict(session, user={})
    return redirect(session['page'])


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
    build_dict(session, user=luser.get())
    return redirect(session['page'])


@app.route('/category/<id>')
def category(id=0):
    if id:
        category = get_category(id)
        if category:
            movies = get_movies_by_category(category.id)
            build_dict(session, page=url_for('category', id=id), search={'movies':{'title': category.name, 'result': [mov.get() for mov in movies]}, 'actors': {'title':'', 'result': []}})
            return render_template('search.html', resources=session)
    build_dict(session, page=url_for('index'))
    return redirect(session['page'])


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('search')
        result = {'movies': [], 'actors': []}
        result['movies'] = {'title': f'Movies: \'{query}\'', 'result': [mov.get() for mov in get_movies(query)]}
        result['actors'] = {'title': f'Actors: \'{query}\'', 'result': [act.get() for act in get_actors(query)]}
        build_dict(session, page='search', search=result, categories=[cat.get() for cat in get_categories()])
        return render_template('search.html', resources=session)
    else:
        build_dict(session, page=url_for('index'))
        return redirect(session['page'])


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

