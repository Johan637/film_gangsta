import os
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

# Sleutel opgeven voor het gebruik van Forms
app.config['SECRET_KEY'] = 'mysecretkey'

# DATABASE en MODELS

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)


class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    director_id = db.Column(db.Integer)
    year = db.Column(db.Integer)


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


class User(db.Model):
    # use me mommy
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)


class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    film_id = db.Column(db.Integer)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    film_id = db.Column(db.Integer)






@app.route('/')
def index():
    return render_template('index.html')


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()

