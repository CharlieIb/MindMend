from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory
from app import app
from app.forms import ChooseForm, LoginForm, ChangePasswordForm, RegisterForm, FormRedirect
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit
from app.utils import HeatMap
from datetime import datetime


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
        if not next_page or urlsplit(next_page).netloc != '':
            if current_user.role == 'Normal':
                next_page = url_for('mind_mirror')
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
# MindMirror - landing page
@app.route('/mindmirror', methods=['GET', 'POST'])
@login_required
def mindmirror():
    now = datetime.now()
    curr_day, curr_month, curr_year = now.day, now.month, now.year

    heatmap = HeatMap(curr_day, curr_month, curr_year)
    month, year = heatmap.month_display(), heatmap.year_display()

    form_display, display = ChooseForm(), 'month'
    if form_display.validate_on_submit():
        if form_display.change.data == 'year':
            display = 'month'
        elif form_display.change.data == 'month':
            display = 'year'

    return render_template(
        'mindmirror.html',
        title='MindMirror',
        curr_day=curr_day,
        curr_month=curr_month,
        curr_year=curr_year,
        month=month,
        year=year,
        display=display,
        form_display=form_display
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
