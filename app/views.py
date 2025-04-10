from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory, session
from app import app
from app import db
from app.forms import ChooseForm, LoginForm, ChangePasswordForm, RegisterForm, FormRedirect, SelectSymptomsForm, \
    generate_form, FormMindMirrorLayout
from app.models import User, EmotionLog
from app.utils import (HeatMap, TrackHealth, symptom_list, questions_database,
                       ConditionManager, ResourceManager, TherapeuticRecManager, TestResultManager,
                       EmotionLogManager, ActivityManager, LocationManager, PersonManager, TrackEmotions)
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime

initialized = False


# Load data into classes on first load
@app.before_request
def initialize():
    global initialized
    if not initialized:
        print("this only happens when the app initializes!")
        # Screening Tool queries
        session = db.session
        try:
            app.condition_manager = ConditionManager(session)
            therapeutic_rec_manager = TherapeuticRecManager(session)
            resource_manager = ResourceManager(session)
            test_result_manager = TestResultManager(session)
            initialized = True
            flash("Data loaded into memory", "success")
        except Exception as e:
            flash(f"Exception: {e}, please restart", "danger")

        # EXAMPLE USAGE OF NEW CLASSES--- DELETE WHEN NOT NEEDED
        cond_id = 1

        # Get a condition and its questions
        condition = app.condition_manager.get_condition(cond_id)
        questions = app.condition_manager.get_questions_for_condition(cond_id)

        # Get therapeutic recommendations and resources for the condition
        recommendations = therapeutic_rec_manager.get_recommendations_for_condition(cond_id)
        resources = resource_manager.get_resources_for_condition(cond_id)

        # Add a test result --- Try not to use too much, now there are like 10 entries of the same result!
        # test_result_manager.add_test_result(user_id=1, cond_id=cond_id, result="Positive")

        # Retrieve test results for a user
        user_test_results = test_result_manager.get_test_results_for_user(user_id=1)

        # The output is from the model classes, use the attribute there to access the data
        # Example
        print(condition.name, condition.threshold)
        for question in questions:
            print(f"{question.q_number}, {question.question}")
        # Try these to get familiar
        print(recommendations)
        print(resources)
        print(user_test_results)

        # DO NOT DELETE! - between the two comments
        if current_user.is_authenticated:
            # Load user log data, if already logged in
            emotion_log_manager = EmotionLogManager(db.session, current_user.id)
            # DO NOT DELETE!

            #### EXAMPLE  USAGE OF EMOTIONLOG CLASS --- CAN DELETE
            logs = emotion_log_manager.emotional_logs
            if not logs:
                print(f"No emotion logs found for user ID {current_user.id}.")
            else:
                print(f"Emotion logs for user ID {current_user.id}:")
                for log in logs.values():
                    print(
                        f"Log ID: {log.log_id}, "
                        f"Emotion: {log.emotion}, "
                        f"Location: {log.location.name if log.location else 'N/A'}, "
                        f"Activity: {log.activity.name if log.activity else 'N/A'}, "
                        f"Person: {log.person.name if log.person else 'N/A'}, "
                        f"Time: {log.time}, "
                        f"Steps: {log.steps}, "
                        f"Notes: {log.free_notes}"
                    )


# Not logged In Access
@app.route('/')
def home():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form_login = LoginForm()
    form_register = FormRedirect()
    if 'submit' in request.form and form_login.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form_login.username.data)
        )
        if user is None or not user.check_password(form_login.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form_login.remember_me.data)
        next_page = request.args.get('next')

        # Load user relevant data
        emotion_log_manager = EmotionLogManager(db.session, current_user.id)
        #### EXAMPLE  USAGE OF EMOTIONLOG CLASS
        logs = emotion_log_manager.emotional_logs
        if not logs:
            print(f"No emotion logs found for user ID {current_user.id}.")
        else:
            print(f"Emotion logs for user ID {current_user.id}:")
            for log in logs.values():
                print(
                    f"Log ID: {log.log_id}, "
                    f"Emotion: {log.emotion}, "
                    f"Location: {log.location.name if log.location else 'N/A'}, "
                    f"Activity: {log.activity.name if log.activity else 'N/A'}, "
                    f"Person: {log.person.name if log.person else 'N/A'}, "
                    f"Time: {log.time}, "
                    f"Steps: {log.steps}, "
                    f"Notes: {log.free_notes}"
                )

        if not next_page or urlsplit(next_page).netloc != '':
            if current_user.role == 'Normal':
                next_page = url_for('mindmirror')
            elif current_user.role == 'Admin':
                next_page = url_for('home_admin', username=current_user.username)
        return redirect(next_page)
    elif 'register' in request.form and form_register.validate_on_submit():
        return redirect(url_for('register'))
    return render_template(
        'login.html',
        title='Sign In',
        form_login=form_login,
        form_register=form_register
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.set_password(form.password.data)
        user.role = 'Normal'

        existing_user = db.session.scalar(sa.select(User).where(User.username == user.username))
        if existing_user:
            flash('Username not available', 'danger')
            return redirect(url_for('register'))
        existing_email = db.session.scalar((sa.select(User).where(User.email == user.email)))
        if existing_email:
            flash('Email already used', 'danger')
            return redirect(url_for('register'))

        db.session.add(user)
        db.session.commit()
        flash('Account created successfully, login to proceed', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# Both logged in and not logged in
@app.route('/contact')
def contacts():
    contacts_info = {
        1: {'name': 'Mischa', 'email': 'mischa.mcla@gmail.com', 'phone': '07501878275'},
        2: {'name': 'Charlie', 'email': '', 'phone': ''},
        3: {'name': 'Feyi', 'email': '', 'phone': ''},
        4: {'name': 'Aravind', 'email': '', 'phone': ''},
        5: {'name': 'Romas', 'email': '', 'phone': ''}
    }
    return render_template('contacts.html', title='Contacts', contacts_info=contacts_info)


# Only Admin Access
@app.route('/admin/<username>')
@login_required
def home_admin(username):
    username = current_user.username
    return render_template('home_admin.html', title=f"Home {username}", username=username)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = ChooseForm()
    if current_user.role != 'Admin':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('home'))

    if form.validate_on_submit():
        try:
            delete_value = int(form.delete.data) if form.delete.data else -1
            change_value = int(form.change.data) if form.change.data else -1
            admin_count = User.query.filter_by(role='Admin').count()

            if (
                    delete_value == current_user.id and admin_count > 1
                    or
                    change_value == current_user.id and admin_count > 1
            ):
                logout_user()

            if delete_value != -1:
                user = User.query.get(delete_value)
                if not user:
                    flash(f"User with ID: {delete_value} does not exist", 'danger')
                    return redirect(url_for('admin'))
                if user.role == 'Admin':
                    if admin_count <= 1:
                        flash('Must have at least one admin', 'danger')
                        return redirect(url_for('admin'))
                db.session.delete(user)
                db.session.commit()
                flash(f"{user.username} has been deleted successfully", 'success')
                return redirect(url_for('admin'))
            elif change_value != -1:
                user = User.query.get(change_value)
                if not user:
                    flash(f"User with ID: {change_value} does not exist", 'danger')
                    return redirect(url_for('admin'))
                if user.role == 'Admin':
                    if admin_count <= 1:
                        flash('Must have at least one admin', 'danger')
                        return redirect(url_for('admin'))
                    user.role = 'Normal'
                else:
                    user.role = 'Admin'
                db.session.commit()
                flash(f"{user.username}'s role has been changed successfully", 'success')
                return redirect(url_for('admin'))
        except Exception as e:
            flash('Error occurred while performing action', 'danger')
            print(f"Error: {e}")

    users = User.query.all()
    headers = ['ID', 'Username', 'Email', 'Role', 'Delete', 'Swap Role']
    return render_template(
        'admin.html',
        title='Admin Page',
        form=form,
        headers=headers,
        users=users
    )


# User Account Functionality Access
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == current_user.username)
        )
        if not user.check_password(form.password.data):
            flash('Invalid password', 'danger')
            return redirect(url_for('change_password'))

        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password has been changed successfully', 'success')
        return redirect(url_for('home'))

    return render_template('change_password.html', title='Change Password', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = FormRedirect()
    if form.validate_on_submit():
        if form.logout.data:
            return redirect(url_for('logout'))
        elif form.change_password.data:
            return redirect(url_for('change_password'))
    return render_template(
        'settings.html',
        title='Settings',
        form=form
    )


# Features
# MindMirror - helper functions
def get_heatmap_info():
    now = datetime.now()
    curr_day, curr_month, curr_year = now.day, now.month, now.year

    # Data would normally get queries from db and passed to HeatMap
    heatmap = HeatMap(curr_day, curr_month, curr_year)
    month, year = heatmap.month_display(), heatmap.year_display()
    months = [
        'January', 'February', 'March',
        'April', 'May', 'June',
        'July', 'August', 'September',
        'October', 'November', 'December'
    ]

    heatmap_info = {
        'curr_day': curr_day,
        'curr_month': curr_month,
        'curr_year': curr_year,
        'month': month,
        'year': year,
        'months': months
    }
    return heatmap_info


def get_health_info():
    # Data would normally get queries from db and passed to TrackHealth
    steps, activity_duration, heart_rate = 6908, 110, [50, 64, 153]
    track_health = TrackHealth(
        steps=steps,
        activity_duration=activity_duration,
        heart_rate=heart_rate
    )
    steps_goal = track_health.steps_goal
    steps_percentage_complete = track_health.steps_percentage_complete()

    activity_duration_goal = track_health.activity_duration_goal
    activity_percentage_complete = track_health.activity_percentage_complete()

    max_heart_rate = track_health.max_heart_rate()
    min_heart_rate = track_health.min_heart_rate()
    avg_heart_rate = track_health.avg_heart_rate()
    heart_rate_range = track_health.heart_rate_range()
    heart_rate_zones = track_health.heart_rate_zones()
    heart_zones_progress_bar = track_health.heart_rate_zone_progress_bar()

    track_health_info = {
        'steps': steps,
        'steps_goal': steps_goal, 'steps_percentage_complete': steps_percentage_complete,
        'activity_duration': activity_duration,
        'activity_duration_goal': activity_duration_goal, 'activity_percentage_complete': activity_percentage_complete,
        'heart_rate': heart_rate,
        'max_heart_rate': max_heart_rate, 'min_heart_rate': min_heart_rate, 'avg_heart_rate': avg_heart_rate,
        'heart_rate_range': heart_rate_range,
        'heart_zones_scaled': heart_zones_progress_bar, 'heart_zones': heart_rate_zones
    }
    return track_health_info


def get_emotions_info():
    # Data would normally get queries from db and passed to TrackEmotions
    track_emotions = TrackEmotions()
    emotion_count = track_emotions.count_emotions()
    total_emotion_logs = sum(info['length'] for info in emotion_count.values())
    emotions_percentage = {
        emotion: {
            'percentage': round(((info['length'] / total_emotion_logs) * 100) / 2),
            'colour': info['colour']
        }
        for emotion, info in emotion_count.items()
    }
    sorted_emotions_percentage = dict(sorted(emotions_percentage.items(), key=lambda item: item[1]['percentage']))
    track_emotions_info = {
        'emotion_count': emotion_count,
        'total_emotion_logs': total_emotion_logs,
        'emotions_percentage_unsorted': emotions_percentage,
        'emotions_percentage': sorted_emotions_percentage,
        'max_num': max(info['length'] for info in emotion_count.values())
    }
    return track_emotions_info


# MindMirror - landing page
@app.route('/mindmirror', methods=['GET', 'POST'])
@login_required
def mindmirror():
    form_display = ChooseForm()
    display_year_month = session.get('display_year_month', 'month')
    if form_display.validate_on_submit():
        if form_display.change.data == 'year':
            display_year_month = 'month'
        elif form_display.change.data == 'month':
            display_year_month = 'year'
        session['display_year_month'] = display_year_month
        return redirect(url_for('mindmirror'))

    heatmap_info = get_heatmap_info()
    heatmap_info['display_year_month'] = display_year_month
    track_health_info = get_health_info()
    track_emotions_info = get_emotions_info()

    if 'mindmirror_display' not in session:
        session['mindmirror_display'] = {
            'heatmap': True,
            'emotion_graph': True,
            'emotion_info': True,
            'track_activity': True,
            'track_steps': True,
            'track_heart_rate': True,
            'heart_zones': True
        }

    return render_template(
        'mindmirror.html',
        title='MindMirror',
        form_display=form_display,
        heatmap_info=heatmap_info,
        mindmirror_display=session.get('mindmirror_display', {}),
        track_health_info=track_health_info,
        track_emotions_info=track_emotions_info
    )


# MindMirror - edit what widgets are shown page
@app.route('/mindmirror_edit', methods=['GET', 'POST'])
def mindmirror_edit():
    form = FormMindMirrorLayout(data=session['mindmirror_display'])
    if form.validate_on_submit():
        session['mindmirror_display'] = {
            'heatmap': form.heatmap.data,
            'emotion_graph': form.emotion_graph.data,
            'emotion_info': form.emotion_info.data,
            'track_activity': form.track_activity.data,
            'track_steps': form.track_steps.data,
            'track_heart_rate': form.track_heart_rate.data,
            'heart_zones': form.heart_zones.data
        }
        return redirect(url_for('mindmirror'))

    return render_template(
        'mindmirror_edit.html',
        title='Edit MindMirror',
        form=form
    )


# CheckIn
@app.route('/check-in')
def emotion_log():
    emotions = [
        {"title": "Anxious", "feelings": ["Nervous", "Overwhelmed", "Irritable", "Restless", "Worried"],
         "border": "border-danger"},
        {"title": "Calm", "feelings": ["Relaxed", "Peaceful", "Content", "At Ease", "Serene"], "border": "border-info"},
        {"title": "Happy", "feelings": ["Joyful", "Excited", "Optimistic", "Grateful", "Energetic"],
         "border": "border-warning"},
        {"title": "Sad", "feelings": ["Down", "Lonely", "Disheartened", "Hopeless", "Heartbroken"],
         "border": "border-success"}
    ]
    return render_template('emotion-log.html', title='Check-In', emotions=emotions)


# Screening Tool

# Function to get condition ids from symptoms selected
def selectConditions(selected_symptoms):
    ### TO-DO: Replace function with actual logic of selecting condition
    conditions = [int(id) for id in selected_symptoms]
    return conditions

def generate_questionnaires(conditions):
    questionnaires = {}  # Dictionary to store the results

    for cond_id in conditions:
        condition = app.condition_manager.get_condition(cond_id)
        questions = app.condition_manager.get_questions_for_condition(cond_id)

        # Store condition info and questions in the dictionary
        questionnaires[cond_id] = {
            'name': condition.name,
            'threshold': condition.threshold,
            'questions': [
                {
                    'q_number': question.q_number,
                    'question': question.question,
                    'value': question.value
                }
                for question in questions
            ]
        }
    return questionnaires

# First Page: Select Symptoms
@app.route('/select_symptoms', methods=['GET', 'POST'])
def select_symptoms():
    form = SelectSymptomsForm()
    form.symptoms.choices = symptom_list
    selected_symptoms = []

    if form.validate_on_submit():
        selected_symptoms = form.symptoms.data
        session['selected_symptoms'] = selected_symptoms  # Store selected_symptoms in flask session

        return redirect(url_for('answer_questionnaire'))
    return render_template('select_symptoms.html', title="Choose Symptoms", form=form)




# Second Page: Answer Questionnaire
@app.route('/answer_questionnaire', methods=['GET', 'POST'])
def answer_questionnaire():
    selected_symptoms = session.get('selected_symptoms')

    conditions = selectConditions(selected_symptoms) # Selects appropriate condition_ids from selects symptoms
    questionnaires = generate_questionnaires(conditions) # Retrieves all questionnaires of corresponding conditions

    # Create Flask Forms
    AnswerQuestionnaireForm = generate_form(questionnaires)
    form = AnswerQuestionnaireForm(obj=None)

    if form.validate_on_submit():
        scores = []

        for cond_id, condition_info in questionnaires.items():
            condition_score = 0
            for index, question in enumerate(condition_info['questions']):
                question_id = f"question_{cond_id}_{index}"
                user_answer = getattr(form, question_id).data
                if user_answer == 'True':
                    condition_score += question['value']

                ### TO-DO: Check Threshold and get necessary actions ###
            scores.append({'condition': condition_info['name'], 'score': condition_score})
        return render_template('results.html', scores=scores, title="Questionnaire Result")
    return render_template('questionnaire.html', questionnaires=questionnaires, title='Questionnaire',
                           form=form, enumerate=enumerate)


# Error handlers
# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403


# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404


@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413


# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500
