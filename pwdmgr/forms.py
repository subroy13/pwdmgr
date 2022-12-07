from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length

class UserSignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    useremail = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])


class UserSigninForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    password = PasswordField('Password', validators=[InputRequired()])
    
