from flask import render_template, request, jsonify
from . import app
from .forms import UserSigninForm, UserSignupForm

@app.route("/")
def home():
    return render_template('index.html')


@app.route('/auth/login/')
def login():
    return render_template('login.html', form = UserSigninForm())

@app.route('/auth/signup/', methods = ['GET', 'POST'])
def signup():
    form = UserSignupForm()
    if request.method == "POST":
        if form.validate():
            return jsonify({"data": form.data, "success": True})
        return jsonify({ "errors": form.errors, "success": False }), 400

    return render_template('signup.html', form = form)
