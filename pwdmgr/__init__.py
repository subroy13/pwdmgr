from flask import Flask

app = Flask(__name__)

from .config import Config
from . import routes

app.config['SECRET_KEY'] = Config.APP_SECRET