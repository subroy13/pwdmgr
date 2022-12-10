import json
from flask import render_template, request, jsonify, session, redirect, url_for
from . import app
from .forms import (
    UserSigninForm, 
    UserSignupForm, 
    CreatePasswordForm, 
    EditPasswordForm,
    ViewPasswordForm,
    DeletePasswordForm
)
from .models import User, Password
from .api.userapi import createNewUser, getUser, getUserById
from .api.passapi import createNewPassword, listAllPasswords

@app.route("/")
def home():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        return redirect(url_for('dashboard'))
    return render_template('index.html', user = None)

@app.route("/dashboard/")
def dashboard():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        pwdlist = listAllPasswords(user)
        viewform = ViewPasswordForm()
        delform = DeletePasswordForm()
        return render_template('dashboard.html', 
            pwdlist = pwdlist, 
            user = user, 
            viewform = viewform,
            delform = delform
        )
    return redirect(url_for('home'))


@app.route('/auth/logout')
def logout():
    session['loggedinuserid'] = None
    return redirect(url_for('home'))


@app.route('/auth/login/', methods = ['GET', "POST"])
def login():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        return redirect(url_for('dashboard'))
    form = UserSigninForm()
    if request.method == "POST":
        if form.validate():
            try:
                # perform the login
                # get the user by username
                user = getUser(form.username.data)
                if user is None:
                    return jsonify({"errors": {"username": ["The specified username does not exist!"]}}), 400
                
                # verify the password
                if not user.verify_password_crypt(form.password.data):
                    return jsonify({ "errors": {"password": ["Invalid credentials!"]} }), 400
                
                # if everything is correct, return the user and set session data
                session['loggedinuserid'] = user.id
                return jsonify({"data": user.serialize() }), 200
                
            except Exception as e:
                return jsonify({"errors": str(e) }), 500
        return jsonify({ "errors": form.errors }), 400

    return render_template('login.html', form = form, user = None)

@app.route('/auth/signup/', methods = ['GET', 'POST'])
def signup():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        return redirect(url_for('dashboard'))
    form = UserSignupForm()
    if request.method == "POST":
        if form.validate():
            try: 
                # create a new user
                user = User(form.username.data, form.useremail.data, form.password.data)
                saved_user = createNewUser(user)

                # if everything is done, set session and return the saved user
                session['loggedinuserid'] = user.id
                return jsonify({"data": saved_user}), 200
            except Exception as e:
                print(e)
                return jsonify({"errors": str(e)}), 500
        return jsonify({ "errors": form.errors }), 400

    return render_template('signup.html', form = form, user = None)


@app.route('/password/add', methods = ['GET', 'POST'])
def add_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = CreatePasswordForm()
        if request.method == "POST":
            if form.validate():
                try: 
                    # try parsing the json sensitive info
                    try:
                        jsoninfo = json.loads(form.sensitiveinfo.data)
                    except Exception as e:
                        return jsonify({"errors": {"sensitiveinfo": ["Must be valid json string"]} }), 400
                    
                    # verify master password
                    try:
                        master_key = user.generateMasterKey(form.masterpwd.data)
                    except Exception as e:
                        return jsonify({"errprs": {"masterpwd": ["Invalid master password"]} }), 400

                    pwd = Password(form.pwdname.data, form.pwdtype.data, user, form.description.data)
                    pwd.addSensitiveInfo(master_key, jsoninfo)
                    pwddata = createNewPassword(pwd)
                    return jsonify({"data": pwddata}), 200
                except Exception as e:
                    print(e)
                    return jsonify({"errors": str(e)}), 500
            return jsonify({ "errors": form.errors }), 400

        return render_template('add_password.html', form = form, user = user)
    return redirect(url_for('home'))


@app.route('/password/edit', methods = ['GET', 'POST'])
def edit_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = EditPasswordForm()
        if form.validate():
            pass 
        return jsonify({ "errors": form.errors }), 400
    return redirect(url_for('home'))


@app.route('/password/delete', methods = ['POST'])
def delete_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = DeletePasswordForm()
        if form.validate():
            pass 
        return jsonify({ "errors": form.errors }), 400
    return redirect(url_for('home'))

@app.route('/password/view', methods = ['POST'])
def view_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = ViewPasswordForm()
        if form.validate():
            pass # TODO: return the json data
        return jsonify({ "errors": form.errors }), 400
    return redirect(url_for('home'))

