from os import urandom

from flask import Flask

# creates and sets up app object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://test:pass@localhost:5432/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = urandom(32)