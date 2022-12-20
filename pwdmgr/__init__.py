import os
from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APP_SECRET")

from .database import Database
appdb = Database()  # Only create on instance of DB class, reuse everywhere as needed

from . import routes
from . import errors