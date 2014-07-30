import psycopg2

from flask import Flask
from flask_peewee.db import Database

app = Flask(__name__)
app.config.from_object('config.Configuration')
app.config['SECRET_KEY'] =  open('.secret_key', 'rb').read()
db = Database(app)
