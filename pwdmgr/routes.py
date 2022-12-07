from flask import render_template, request, jsonify
from . import app
from .forms import UserSigninForm, UserSignupForm
from .models import User
from .api.userapi import createNewUser, getUser

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/dashboard/")
def dashboard():
    return render_template('dashboard.html')


@app.route('/auth/login/')
def login():
    form = UserSigninForm()
    if request.method == "POST":
        if form.validate():
            try:
                # perform the login
                # get the user by username
                user = getUser(form.username.data)
                if user is None:
                    return jsonify({"errors": "The specified username does not exist!"}), 404
                
                # verify the password
                if not user.verify_password_crypt(form.password.data):
                    return jsonify({ "errors": "Invalid credentials!" }), 401
                
                # if everything is correct, return the user
                return jsonify({"data": user.serialize() }), 200
                
            except Exception as e:
                return jsonify({"errors": str(e) }), 500
        return jsonify({ "errors": form.errors }), 400

    return render_template('login.html', form = form)

@app.route('/auth/signup/', methods = ['GET', 'POST'])
def signup():
    form = UserSignupForm()
    if request.method == "POST":
        if form.validate():
            try: 
                # create a new user
                user = User(form.username.data, form.useremail.data, form.password.data)
                saved_user = createNewUser(user)
                return jsonify({"data": saved_user}), 200
            except Exception as e:
                return jsonify({"errors": str(e)}), 500
        return jsonify({ "errors": form.errors }), 400

    return render_template('signup.html', form = form)
