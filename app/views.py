from flask import render_template, redirect, url_for, flash, request, session
from app import app
from app import db
from app.utils.General import (ChooseForm, LoginForm, ChangePasswordForm, RegisterForm, SettingsForm,
                               SelectSymptomsForm, generate_form, MindMirrorLayoutForm, EmotionForm, EmotionNoteForm,
                               roles_required, get_emotions_info, get_health_info, get_heatmap_info, initialize_app,
                               symptom_list,
                               selectConditions, generate_questionnaires)
from app.utils import EmotionLogManager, ActivityManager, LocationManager, PersonManager
from app.utils.MindMirror.notification_service import NotificationService
from app.models import User, Notification
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from app.utils.CheckIn.EmotionLog import emotions


# Load data into classes on first load
@app.before_request
def before_request_handler():
    initialize_app(app)


# Not logged In Access
@app.route('/')
def home():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form_login = LoginForm()
    form_register = SettingsForm()
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
        app.emotion_log_manager = EmotionLogManager(db.session, current_user.id)
        #### EXAMPLE  USAGE OF EMOTIONLOG CLASS
        logs = app.emotion_log_manager.emotional_logs
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
        existing_email = db.session.scalar(sa.select(User).where(User.email == user.email))
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
        2: {'name': 'Charlie', 'email': 'cibbett325@gmail.com', 'phone': 'N/A'},
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
@roles_required('Admin')
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
    form = SettingsForm()
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


@app.route('/track_physiological', methods=['GET', 'POST'])
@login_required
def track_physiological():
    user = db.session.scalar(sa.select(User).where(User.username == current_user.username))
    user.track_physiological = not user.track_physiological
    db.session.commit()
    flash(f"Your physiological is being tracked: {current_user.track_physiological}", 'success')
    return redirect(url_for('settings'))


@app.route('/share_data', methods=['GET', 'POST'])
@login_required
def share_data():
    user = db.session.scalar(sa.select(User).where(User.username == current_user.username))
    user.share_data = not user.share_data
    db.session.commit()
    flash(f"Your data is being shared: {current_user.share_data}", 'success')
    return redirect(url_for('settings'))


####################################################### FEATURES #######################################################

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

    service = NotificationService(db.session)
    limit = int(request.args.get('limit', 5))
    notification_info = service.get_notifications(limit)

    return render_template(
        'mindmirror.html',
        title='MindMirror',
        form_display=form_display,
        heatmap_info=heatmap_info,
        mindmirror_display=current_user.user_settings.mind_mirror_display,
        track_health_info=track_health_info,
        track_emotions_info=track_emotions_info,
        notification_info=notification_info
    )


# MindMirror - edit what widgets are shown page
@app.route('/mindmirror_edit', methods=['GET', 'POST'])
@login_required
def mindmirror_edit():
    mind_mirror_display = current_user.user_settings.mind_mirror_display
    form = MindMirrorLayoutForm(data=mind_mirror_display)
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == current_user.username))
        user.user_settings.mind_mirror_display = {
            'heatmap': form.heatmap.data,
            'emotion_graph': form.emotion_graph.data,
            'emotion_info': form.emotion_info.data,
            'track_activity': form.track_activity.data,
            'track_steps': form.track_steps.data,
            'track_heart_rate': form.track_heart_rate.data,
            'heart_zones': form.heart_zones.data
        }
        db.session.commit()
        flash('MindMirror layout updated successfully!', 'success')
        return redirect(url_for('mindmirror'))

    return render_template(
        'mindmirror_edit.html',
        title='Edit MindMirror',
        form=form
    )


@app.route('/notification_seen')
@login_required
def notification_seen():
    notif_id = int(request.args.get('notif_id'))
    notif = db.session.get(Notification, notif_id)
    notif.is_read = True
    db.session.commit()

    limit = request.args.get('limit', 15)
    is_open = request.args.get('is_open', 'false')

    return redirect(
        url_for('mindmirror', limit=limit, is_open=is_open)
    )


# CheckIn
@app.route('/check-in', methods=['GET', 'POST'])
@login_required
def emotion_log():
    form = EmotionForm()

    form.emotions.choices = [
        (f"{feeling}::{emotion['title']}", feeling)
        for emotion in emotions
        for feeling in emotion["feelings"]
    ]

    if form.validate_on_submit():
        session['selected_emotions'] = form.emotions.data
        return redirect(url_for('emotion_details'))

    return render_template('emotion-log.html', title='Check-In', emotions=emotions, form=form)


# Add Extra details to check in
@app.route('/emotion-details', methods=['GET', 'POST'])
@login_required
def emotion_details():
    form = EmotionNoteForm()
    selected_emotions = session.get('selected_emotions')

    if not selected_emotions:
        flash("Please select emotions first.")
        return redirect(url_for('emotion_log'))

    if form.validate_on_submit():
        manager = EmotionLogManager(session=db.session, user_id=current_user.id)
        activity_manager = ActivityManager(session=db.session)
        person_manager = PersonManager(session=db.session)
        location_manager = LocationManager(session=db.session)

        activity_id = activity_manager.get_activity_id_by_name(form.activity.data)
        person_id = person_manager.get_person_id_by_name(form.person.data)
        location_id = location_manager.get_location_id_by_name(form.location.data)

        for val in selected_emotions:
            feeling, _ = val.split("::")
            manager.add_new_log(
                emotion=feeling,
                steps=0,
                free_notes=form.notes.data,
                activity_id=activity_id,
                person_id=person_id,
                location_id=location_id
            )

        session.pop('selected_emotions', None)
        flash("Successfully saved!", "success")
        return redirect(url_for('mindmirror'))

    return render_template('emotion_details.html', title="Tell us more", form=form)


# Screening Tool
# Landing Page: Page for user to select Presenting Symptoms
@app.route('/select_symptoms', methods=['GET', 'POST'])
@login_required
def select_symptoms():
    # Creates Flask Form containing symptoms as options to select from
    form = SelectSymptomsForm()
    form.symptoms.choices = symptom_list

    if form.validate_on_submit():
        selected_symptoms = form.symptoms.data
        session['selected_symptoms'] = selected_symptoms  # Store user selected symptoms in flask session

        return redirect(url_for('answer_questionnaire'))
    return render_template('select_symptoms.html', title="Choose Symptoms", form=form)


# Second Page: Page for user to answer given questionnaire
@app.route('/answer_questionnaire', methods=['GET', 'POST'])
@login_required
def answer_questionnaire():
    # Initialize session results
    if 'results' not in session:
        session['results'] = []
        session.modified = True

    selected_symptoms = session.get('selected_symptoms')  # Loads previously selected symptoms by user
    conditions = selectConditions(selected_symptoms)  # Selects appropriate condition_ids from selected symptoms

    current_index = int(request.args.get('index', 0))
    if current_index == 0:
        session['results'] = []  # Reset scores for new attempt
    if current_index >= len(conditions):
        results = session.pop('results', [])  # Clear session storage
        return render_template('results.html', results=results, title="Questionnaire Result")

    # Creates new flask form for each condition
    cond_id = conditions[current_index]
    questionnaire = generate_questionnaires(cond_id)
    AnswerQuestionnaireForm = generate_form(questionnaire)
    form = AnswerQuestionnaireForm(obj=None)

    if form.validate_on_submit():
        condition_score = 0
        for q_index, question in enumerate(questionnaire['questions']):
            field_name = f"question_{questionnaire['id']}_{q_index}"
            user_answer = getattr(form, field_name).data  # Gets User response for question
            if user_answer == 'True':
                condition_score += question['value']  # Adds question score if marked as 'True'

        # Retrieve and store condition information and user score
        cond_obj = app.condition_manager.get_condition(cond_id)
        # Convert SQLAlchemy objects to dictionaries as flask session cannot store SQLAlchemy objects
        recs = [
            {'description': rec.description, 'treatments': rec.treatments}
            for rec in app.therapeutic_rec_manager.get_recommendations_for_condition(cond_id)
        ]
        rsrcs = [
            {'label': rsrc.label, 'link': rsrc.link}
            for rsrc in app.resource_manager.get_resources_for_condition(cond_id)
        ]
        threshold_met = (condition_score > cond_obj.threshold)
        result = {
            'condition': cond_obj.name,
            'score': condition_score,
            'is_met_threshold': threshold_met,
            'therapeutic_recs': recs,
            'resources': rsrcs
        }
        session['results'].append(result)
        session.modified = True

        # Move to next condition or render results
        next_index = current_index + 1
        if next_index < len(conditions):
            return redirect(url_for('answer_questionnaire', index=next_index))
        else:
            results = session.pop('results', [])  # Clear session and get results
            return render_template('results.html', title="Questionnaire Result", results=results)

    return render_template('questionnaire.html', title='Questionnaire', form=form, questionnaires=questionnaire,
                           current_index=current_index, conditions=conditions, enumerate=enumerate)


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
