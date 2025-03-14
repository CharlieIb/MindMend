from flask_wtf import FlaskForm
from wtforms import (SubmitField, HiddenField, StringField, PasswordField,
                     BooleanField, IntegerField, ValidationError, EmailField)
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo
from email_validator import validate_email, EmailNotValidError
import re


# Validators
def validate_password_complexity(form, field):
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')


def valid_email(form, field):
    email = field.data
    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise ValidationError(f"Email not valid: {e}")

    if not email.lower().endswith('.ac.uk'):
        raise ValidationError('Must be a university email.')


# Forms
class ChooseForm(FlaskForm):
    delete = HiddenField('Choice')
    change = HiddenField('Choice')


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), valid_email])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        validate_password_complexity
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        validate_password_complexity
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match'),
    ])
    submit = SubmitField('Update Password')


class FormRedirect(FlaskForm):
    register = SubmitField('Register')
    logout = SubmitField('Logout')
    change_password = SubmitField('Change Password')
