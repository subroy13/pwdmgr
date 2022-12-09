import json
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, EqualTo, Length, Optional
from wtforms.widgets import TextArea

class UserSignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    useremail = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])


class UserSigninForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    password = PasswordField('Password', validators=[InputRequired()])
    

class CreatePasswordForm(FlaskForm):
    pwdname = StringField('Password Name', validators=[InputRequired()])
    pwdtype = StringField('Password Group', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    sensitiveinfo = TextAreaField('Password Information', validators=[InputRequired()])
    masterpwd = PasswordField('Master Password', validators=[InputRequired()])


class EditPasswordForm(FlaskForm):
    pwdid = HiddenField('Password Id', validators=[InputRequired()])
    pwdname = StringField('Password Name', validators=[InputRequired()])
    pwdtype = StringField('Password Group', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    sensitiveinfo = TextAreaField('Password Information', validators=[InputRequired()])
    masterpwd = PasswordField('Master Password', validators=[InputRequired()])

