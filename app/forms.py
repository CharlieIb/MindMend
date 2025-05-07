from flask_wtf import FlaskForm
from wtforms import (SubmitField, HiddenField, StringField, PasswordField,
                     BooleanField, ValidationError, EmailField, RadioField)
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from email_validator import validate_email, EmailNotValidError
from wtforms.fields.choices import SelectMultipleField, SelectField
from wtforms.widgets.core import ListWidget, CheckboxInput
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


class SettingsForm(FlaskForm):
    register = SubmitField('Register')
    logout = SubmitField('Logout')
    change_password = SubmitField('Change Password')


class MindMirrorLayoutForm(FlaskForm):
    heatmap = BooleanField('Check In Activity Heatmap', default=True)
    emotion_graph = BooleanField('Emotion Graph', default=True)
    emotion_info = BooleanField('Emotion Info', default=True)
    track_activity = BooleanField('Track Activity', default=False)
    track_steps = BooleanField('Track Steps', default=False)
    track_heart_rate = BooleanField('Track Heart Rate', default=False)
    track_blood_pressure = BooleanField('Blood Pressure', default=False)
    heart_zones = BooleanField('Heart Zones', default=False)
    submit = SubmitField('Submit')


# Forms for screening tool
class SelectSymptomsForm(FlaskForm):
    symptoms = SelectMultipleField('Select Symptoms', choices=[],
                                   validators=[DataRequired(message='Please select at least 1 option')],
                                   widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    submit = SubmitField('Submit')

def generate_form(questionnaires):
    class AnswerQuestionnaireForm(FlaskForm):
        pass  # Fields will be added dynamically

    # Create new radio field for each question in this condition
    for index,question in enumerate(questionnaires['questions']):
            question_id = f"question_{questionnaires['id']}_{index}"
            setattr(
                AnswerQuestionnaireForm,
                question_id,
                RadioField(
                    question['question'],
                    choices=['True', 'False'],
                    validators=[DataRequired(message="Please answer question")]
                )
            )
    setattr(AnswerQuestionnaireForm, 'submit', SubmitField('Submit'))
    return AnswerQuestionnaireForm

class EmotionForm(FlaskForm):
    emotions = SelectMultipleField(
        'Emotions',
        choices=[],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    submit = SubmitField('Next')

class EmotionNoteForm(FlaskForm):
    notes = TextAreaField("How are you feeling?", validators=[Optional()])
    activity = SelectField(
        'What activity were you doing at the time?',
        choices=[('N/A', 'N/A'), ('Working', 'Working'), ('Commuting', 'Commuting'), ('Socialising', 'Socialising'), ('Exercising', 'Exercising'), ('Studying', 'Studying'), ('Shopping', 'Shopping'), ('Relaxing', 'Relaxing')]
    )
    location = SelectField(
        'Where were you?',
        choices=[('N/A', 'N/A'), ('Office', 'Office'), ('Home', 'Home'), ('Bar', 'Bar'), ('Gym', 'Gym'), ('Park', 'Park'), ('Cafe', 'Cafe'), ('Library', 'Library') ]
    )
    person = SelectField(
        'Who were you with?',
        choices=[('N/A', 'N/A'), ('Colleagues', 'Colleagues'), ('Friends', 'Friends'), ('Family', 'Family'), ('Partner', 'Partner'), ('Neighbours', 'Neighbours'), ('Strangers', 'Strangers')]
    )
    submit = SubmitField("Save")


