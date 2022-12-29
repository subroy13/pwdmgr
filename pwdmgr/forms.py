from flask_wtf import FlaskForm
from wtforms import (
    StringField, EmailField, PasswordField, 
    TextAreaField, HiddenField, BooleanField,
    ValidationError
)
from wtforms.validators import InputRequired, EqualTo, Length, Optional, Regexp

######################
# VALIDATORS 
#####################
class NotEqualTo(object):  # --> Change to 'LessThan'
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data == other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext('Field must not be equal to %(other_name)s.')
            raise ValidationError(message % d)

########################
# FORMS 
########################




class UserSignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    useremail = EmailField('Email', validators=[InputRequired(), Regexp(r"[a-zA-Z0-9\.\-\_]+\@[a-zA-Z0-9\.\-\_]+\.[a-zA-Z]", message="Invalid email address")])
    password = PasswordField('Master Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])


class UserSigninForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 15)])
    password = PasswordField('Master Password', validators=[InputRequired()])
    mfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])
    
class UserDeleteForm(FlaskForm):
    delpassword = PasswordField('Master Password', validators=[InputRequired()])
    delmfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])
    softdelete = BooleanField('Is soft deleted?', validators=[InputRequired()])

class CreatePasswordForm(FlaskForm):
    pwdname = StringField('Credentials Name', validators=[InputRequired()])
    pwdtype = StringField('Credentials Group', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    sensitiveinfo = TextAreaField('Credentials Information', validators=[InputRequired()])
    masterpwd = PasswordField('Master Password', validators=[InputRequired()])
    mfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])


class EditPasswordForm(FlaskForm):
    pwdid = HiddenField('Credentials Id', validators=[InputRequired()])
    pwdname = StringField('Credentials Name', validators=[InputRequired()], render_kw={'disabled':''})
    pwdtype = StringField('Credentials Group', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    masterpwd = PasswordField('Master Password', validators=[InputRequired()])
    mfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])

class ViewPasswordForm(FlaskForm):
    viewpwdid = HiddenField('Credentials Id', validators=[InputRequired()])
    viewmasterpwd = PasswordField('Master Password', validators=[InputRequired()])
    viewmfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])

class DeletePasswordForm(FlaskForm):
    delpwdid = HiddenField('Credentials Id', validators=[InputRequired()])
    delmasterpwd = PasswordField('Master Password', validators=[InputRequired()])
    delmfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])

class ChangeMasterPasswordForm(FlaskForm):
    oldpass = PasswordField('Old Master Password', validators=[InputRequired()])
    mfa = StringField('MFA Code', validators=[InputRequired(), Length(min = 6, max = 6)])
    newpass = PasswordField('New Master Password', validators=[InputRequired(), NotEqualTo('oldpass', message = 'New password must not be same as old password')])
    confirm_newpass = PasswordField('Confirm New Master Password', validators=[InputRequired(), EqualTo('newpass')])