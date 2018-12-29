import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from .create_app import app

# connects app to sqlalchemy and sets up for migration if it's necessary
db = SQLAlchemy(app)
migrate = Migrate(app, db)


db_session = db.session


# creates database if one does not already exist
def create_all():
    db.create_all()


# class that maps User objects to records of table users
# id is the primary key for record in database, created at time of commit, is integer
# name is stared as a string
# email is stored as a string, must be unique
# password stored as string, not encrypted in this implementation
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))


# Class that maps Entry objects to records of table entries
# id is the primary key for record in database, created at time of commit, is integer
# title is stored as string
# datetime is time when entry was created, automatically specified
# user_id establishes many to one relationship with users. Older entries may not have user_id for legacy reasons, but
# all new Entry objects should include this
class Entry(db.Model):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    title = Column(String(1024))
    content = Column(Text)
    datetime = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
