from flask import render_template
from . import app
from .forms import UserSigninForm, UserSignupForm

@app.route("/")
def home():
    return render_template('index.html')


@app.route('/auth/login/')
def login():
    return render_template('login.html', form = UserSigninForm())

@app.route('/auth/signup/')
def signup():
    return render_template('signup.html', form = UserSignupForm())
