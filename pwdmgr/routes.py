import json
from flask import render_template, request, jsonify, session, redirect, url_for
from . import app
from .forms import (
    UserSigninForm, 
    UserSignupForm, 
    UserDeleteForm,
    CreatePasswordForm, 
    EditPasswordForm,
    ViewPasswordForm,
    DeletePasswordForm
)
from .models import User, Password
from .api.userapi import createNewUser, getUser, getUserById, deleteUser, softDeleteUser
from .api.passapi import (
    createNewPassword, 
    listAllPasswords, 
    updatePassword, 
    deletePassword,
    getPasswordById,
    viewPassword
)

@app.route("/")
def home():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        return redirect(url_for('dashboard'))
    return render_template('index.html', user = None)

@app.route("/dashboard/")
def dashboard():
    print(session)
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
                        return jsonify({"errors": {"masterpwd": ["Invalid master password"]} }), 400

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
        if request.method == "POST":
            if form.validate():
                try:                     
                    # verify edit password for logged in user or not
                    oldpwd = getPasswordById(form.pwdid.data)
                    if oldpwd is None:
                        return jsonify({ "errors": "Password not found" }), 404
                    if oldpwd.auth_user.id != user.id:
                        # invalid user, not authorized
                        return jsonify({ "errors": "User is unauthorized to perform this action" }), 401

                    # verify master password
                    try:
                        master_key = user.generateMasterKey(form.masterpwd.data)
                    except Exception as e:
                        return jsonify({"errors": {"masterpwd": ["Invalid master password"]} }), 400

                    oldpwd.pwdtype = form.pwdtype.data
                    oldpwd.description = form.description.data
                    pwddata = updatePassword(oldpwd)
                    return jsonify({"data": pwddata}), 200
                except Exception as e:
                    print(e)
                    return jsonify({"errors": str(e)}), 500
            return jsonify({ "errors": form.errors }), 400
        else:
            pwdid = request.args.get("id")
            if pwdid is None:
                return jsonify({ "errors": "Invalid id field for password" }), 400
            pwd = getPasswordById(pwdid)
            if pwd is None:
                return jsonify({ "errors": "Password not found" }), 404
            form.pwdid.data = pwdid
            form.pwdname.data = pwd.pwdname
            form.pwdtype.data = pwd.pwdtype
            form.description.data = pwd.description
            return render_template('edit_password.html', form = form, user = user)
    return redirect(url_for('home'))

@app.route('/password/edit/sensitiveinfo', methods = ['POST'])
def password_edit_sensitiveinfo():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        if request.method == "POST":
            jsondata = request.get_json()
            try:                     
                # verify edit password for logged in user or not
                oldpwd = getPasswordById(jsondata["pwdid"])
                if oldpwd is None:
                    return jsonify({ "errors": "Password not found" }), 404
                if oldpwd.auth_user.id != user.id:
                    # invalid user, not authorized
                    return jsonify({ "errors": "User is unauthorized to perform this action" }), 401

                # verify master password
                try:
                    master_key = user.generateMasterKey(jsondata["masterpwd"])
                except Exception as e:
                    return jsonify({"errors": {"viewmasterpwd": ["Invalid master password"]} }), 400

                try:
                    sensitiveinfo = json.loads(jsondata["sensitiveinfo"])
                except Exception as e:
                    return jsonify({"errors": {"passwordviewarea": ["Invalid json string"]}}), 400

                oldpwd.addSensitiveInfo(master_key, sensitiveinfo)
                pwddata = updatePassword(oldpwd)
                return jsonify({"data": pwddata}), 200
            except Exception as e:
                print(e)
                return jsonify({"errors": str(e)}), 500

    return redirect(url_for('home'))



@app.route('/password/delete', methods = ['POST'])
def delete_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = DeletePasswordForm()
        if request.method == "POST":
            if form.validate():
                try:
                    pwd = getPasswordById(form.delpwdid.data)
                    if pwd is None:
                        return jsonify({"errors": "Password not found"}), 404
                    if pwd.auth_user.id != user.id:
                        return jsonify({"errors": "User is unauthorized to perform this action" }), 401
                    master_key = pwd.auth_user.generateMasterKey(form.delmasterpwd.data)
                except Exception as e:
                    # unauthorized user
                    return jsonify({"errors": {"delmasterpwd": ["Invalid master password"]}}), 400
                res = deletePassword(form.delpwdid.data)  # do the delete now
                return jsonify({"data": pwd.serialize() }), 200
            return jsonify({ "errors": form.errors }), 400
    return redirect(url_for('home'))

@app.route('/password/view', methods = ['POST'])
def view_password():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = ViewPasswordForm()
        if request.method == "POST":
            if form.validate():
                jsonobj = viewPassword(form.viewpwdid.data, form.viewmasterpwd.data)
                if jsonobj is None:
                    # unauthorized user
                    return jsonify({"errors": {"viewmasterpwd": ["Invalid master password"]}}), 400
                return jsonify({"data": jsonobj}), 200
            return jsonify({ "errors": form.errors }), 400
    return redirect(url_for('home'))

@app.route('/user/setting', methods = ["GET", "POST"])
def user_settings():
    if 'loggedinuserid' in session and session['loggedinuserid'] is not None:
        user = getUserById(session['loggedinuserid'])
        form = UserDeleteForm()
        if request.method == "POST":
            if form.validate():
                print(form.softdelete.data)
                if not user.verify_password_crypt(form.password.data):
                    return jsonify({"errors": {"password": ["Invalid login password"]}}), 400
                try:
                    if form.softdelete.data:
                        softDeleteUser(form.userid.data)
                    else:
                        deleteUser(form.userid.data)
                    del session['loggedinuserid']
                    return jsonify({"data": user.serialize() }), 200
                except Exception as e:
                    return jsonify({"errors": str(e)}), 500
            else:
                return jsonify({"errors": form.errors}), 400
        return render_template('user_settings.html', user = user, form = form)
    else:
        return redirect(url_for('home'))

