import os
from flask import render_template, request, redirect, url_for, session
import bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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
    thumbnail = db.Column(db.String(128))

    def __init__(self, firstname, lastname, thumbnail):
        self.firstname = firstname
        self.lastname = lastname
        self.thumbnail = thumbnail

    def get(self):
        return {'id': self.id, 'firstname': self.firstname, 'lastname': self.lastname, 'thumbnail': self.thumbnail}

    def name(self):
        return self.firstname +' ' + self.lastname


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

    def name(self):
        return self.firstname +' ' + self.lastname


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


def get_row(table, **kwargs):
    row = db.session.execute(db.select(table).filter_by(**kwargs)).scalars().first()
    return row


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


def get_join(table1, table2, **kwargs):
    rows = [row[1] for row in db.session.query(table1, table2).filter_by(**kwargs).join(table2).all()]
    return rows


def get_users(name="", email=""):
    users = None
    if name:
        users = db.session.execute(db.select(User).filter_by(name=name)).scalars().all()
    elif email:
        users = db.session.execute(db.select(User).filter_by(email=email)).scalars().all()
    else:
        users = db.session.execute(db.select(User)).scalars().all()
    return users


def get_directors(name = ''):
    directors = []
    if name:
        directors.extend(db.session.execute(db.select(Director).filter_by(firstname=name)).scalars().all())
        directors.extend(db.session.execute(db.select(Director).filter_by(lastname=name)).scalars().all())
    else:
        directors = db.session.execute(db.select(Director)).scalars().all()
    return directors



def create_user(email, name, password):
    if get_users(name=name) or get_users(email=email):
        return
    salt = bcrypt.gensalt()
    user = User(email, name, bcrypt.hashpw(password.encode('utf8'), salt).decode('utf-8'))
    db.session.add(user)
    db.session.commit()


def build_dict(dict, **kwargs):
    for kw, arg in kwargs.items():
        dict[kw] = arg


def build_result(mtitle='', atitle='',dtitle= '', movies=[], actors=[], directors=[]):
    dict = {}
    dict['m_title'] = mtitle
    dict['a_title'] = atitle
    dict['d_title'] = dtitle
    dict['movies'] = movies
    dict['actors'] = actors
    dict['directors'] = directors
   
    return dict

# Page routing


@app.route('/')
def index():
    movies = get_movies()
    result = build_result('Home', movies=[mov.get() for mov in movies])
    categories = [cat.get() for cat in get_categories()]
    build_dict(session, page=url_for('index'))
    return render_template("index.html", categories=categories, result=result)



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
        if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf-8')):
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
        if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf-8')):
            luser = user
            break
    if not luser:
        print('false login')
    build_dict(session, user=luser.get())
    return redirect(session['page'])


@app.route('/category/<id>')
def category(id):
    if id:
        category = get_row(Category, id=id)
        if category:
            movies = get_join(Film_Category, Film, category_id=category.id)
            result = build_result(category.name, movies=[mov.get() for mov in movies])
            categories = [cat.get() for cat in get_categories()]
            build_dict(session, page=url_for('category', id=id))
            return render_template('search.html', categories=categories, result=result)
    build_dict(session, page=url_for('index'))
    return redirect(session['page'])


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        query = request.form.get('search')
        result = build_result(f'Movies: \'{query}\'', f'Actors: \'{query}\'', f'Directors:\'{query}\'',[mov.get() for mov in get_movies(query)], [act.get() for act in get_actors(query)], [dir.get() for dir in get_directors(query)])
        build_dict(session, page='search')
        categories=[cat.get() for cat in get_categories()]
        return render_template('search.html', categories=categories, result=result)
    else:
        build_dict(session, page=url_for('index'))
        return redirect(session['page'])


@app.route('/actor/<id>')
def actor(id):
    actor = get_row(Actor, id=id)
    movies = get_join(Role, Film, actor_id=id)
    result = build_result(actor.name(), movies=[mov.get() for mov in movies])
    categories = [cat.get() for cat in get_categories()]
    build_dict(session, page=url_for('actor', id=id))
    return render_template('search.html', categories=categories, result=result)



@app.route('/film/<id>', methods=['POST', 'GET'])
def film(id):
    film = get_row(Film, id=id)
    movie = film.get()
    build_dict(session, page=url_for('film', id=id))
    categories = [cat.get() for cat in get_categories()]
    return render_template('film.html', categories=categories, film=movie, director=get_row(Director, id=film.director_id).name())


@app.route('/director/<id>')
def director(id):
    movies = get_join(Director, Film, id=id)
    result = build_result('Director', movies=[mov.get() for mov in movies])
    build_dict(session, page=url_for('director', id=id))
    categories = [cat.get() for cat in get_categories()]
    return render_template('film.html', categories=categories, result=result)



@app.route('/movies')
def movies():
    result = build_result('Movies', movies=[mov.get() for mov in get_movies()])
    build_dict(session, page=url_for('movies'))
    categories = [cat.get() for cat in get_categories()]
    return render_template('search.html', result=result, categories=categories)


@app.route('/actors')
def actors():
    result = build_result(atitle='Actors', actors=[act.get() for act in get_actors()])
    build_dict(session, page=url_for('actors'))
    categories = [cat.get() for cat in get_categories()]
    return render_template('search.html', result= result, categories=categories)


@app.route('/directors')
def directors():
    result = build_result(dtitle='Directors', directors=[act.get() for act in get_directors()])
    build_dict(session, page=url_for('directors'))
    categories = [cat.get() for cat in get_categories()]
    return render_template('search.html', result=result, categories=categories)



with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

