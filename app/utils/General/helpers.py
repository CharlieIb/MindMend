from app import app
from app import db
from app.utils import (ConditionManager, ResourceManager, TherapeuticRecManager, TestResultManager, EmotionLogManager,
                       ActivityManager, LocationManager, PersonManager, HeatMap, TrackHealth)
from app.models import User, Notification, EmotionLog
from functools import wraps
from flask import abort, flash
from flask_login import current_user
import sqlalchemy as sa
from datetime import datetime, timedelta
from collections import Counter


#################### GENERAL ####################
# Defines a decorator that specifies roles allowed for a route --- move to helper.py folder?
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator


#################### Initializing App ####################
initialized = False


def initialize_app(app):
    global initialized
    if not initialized:
        print("Initializing application managers...")
        try:
            # Initialize all managers
            app.condition_manager = ConditionManager(db.session)
            app.therapeutic_rec_manager = TherapeuticRecManager(db.session)
            app.resource_manager = ResourceManager(db.session)
            app.test_result_manager = TestResultManager(db.session)
            if current_user.is_authenticated:
                # Load user log data, if already logged in
                app.emotion_log_manager = EmotionLogManager(db.session, current_user.id)
            initialized = True
            flash("Application data loaded into memory", "success")

            # Debug/demo code (remove in production)
            _demo_managers(app)

        except Exception as e:
            flash(f"Initialization failed: {str(e)}", "danger")
            raise


def _demo_managers(app):
    """Demo/test function for the managers (remove in production)"""
    # cond_id = 1
    #
    # # Demo condition manager
    # condition = app.condition_manager.get_condition(cond_id)
    # questions = app.condition_manager.get_questions_for_condition(cond_id)
    #
    # # Demo other managers
    # recommendations = app.therapeutic_rec_manager.get_recommendations_for_condition(cond_id)
    # resources = app.resource_manager.get_resources_for_condition(cond_id)
    # user_test_results = app.test_result_manager.get_test_results_for_user(user_id=1)
    #
    # print(f"Demo:\n{condition.name}\n{questions}\n{recommendations}\n{resources}\n{user_test_results}")


#################### MindMirror ####################
def get_heatmap_info():
    now = datetime.now()
    curr_day, curr_month, curr_year = now.day, now.month, now.year

    data_log = [
        {'date': log.time, 'emotion': log.emotion}
        for log in current_user.emotion_logs
    ]

    heatmap = HeatMap(curr_day, curr_month, curr_year, data_log)
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

    # Basic Implementation - if no aged saved / logged
    age = track_health.age

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
        'heart_zones_scaled': heart_zones_progress_bar, 'heart_zones': heart_rate_zones,
        'age': age
    }
    return track_health_info


def get_emotions_info_from_logs(logs):
    default_emotions = {'Anger': 0, 'Anxious': 0, 'Sad': 0, 'Happy': 0, 'Love': 0, 'Calm': 0}

    try:
        emotions = default_emotions.copy()
        for log in logs:
            emotions[log.emotion] = emotions.get(log.emotion, 0) + 1

        total_emotions = sum(emotions.values())

        if total_emotions:
            emotions_percentage = {
                emotion: round((count / total_emotions * 100) / 2)
                for emotion, count in emotions.items()
            }

            max_emotion, max_value = max(emotions_percentage.items(), key=lambda item: item[1], default=(None, 0))
            max_num = [max_emotion, max_value * 2]

            segments = []
            cumulative = 0
            items = list(emotions_percentage.items())
            for idx, (emo, val) in enumerate(items):
                cumulative += val
                cumulative = min(50, cumulative)
                if idx == len(items) - 1:
                    cumulative = 50
                segments.append({
                    'emotion': emo,
                    'value': val,
                    'cumulative': cumulative
                })
        else:
            emotions_percentage = default_emotions.copy()
            segments = [
                {'emotion': emotion, 'value': 0, 'cumulative': -1}
                for emotion in default_emotions
            ]
            max_num = [None, 0]

        return {
            'emotions': emotions,
            'total_emotion_logs': total_emotions,
            'emotions_percentage': emotions_percentage,
            'segments': segments,
            'max_num': max_num
        }

    except Exception as e:
        print(f"Error: {e}")
        emotions = default_emotions.copy()
        emotions_percentage = default_emotions.copy()
        segments = [
            {'emotion': emotion, 'value': 0, 'cumulative': 0}
            for emotion in default_emotions
        ]
        return {
            'emotions': emotions,
            'total_emotion_logs': 0,
            'emotions_percentage': emotions_percentage,
            'segments': segments,
            'max_num': [None, 0]
        }


def get_emotions_info():
    return get_emotions_info_from_logs(current_user.emotion_logs)


def should_notify(latest_time, period_days=1):
    return (datetime.utcnow() - latest_time) >= timedelta(days=period_days)


def create_notification(message, frequency):
    notif = Notification(
        user_id=current_user.id,
        time=datetime.utcnow(),
        message=message,
        frequency=frequency
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def get_last_notification_time(frequency: str):
    return db.session.scalar(
        sa.select(Notification.time)
        .where(
            Notification.user_id == current_user.id,
            Notification.frequency == frequency
        )
        .order_by(Notification.time.desc())
        .limit(1)
    )


def get_last_notifications(limit: int):
    stmt = (
        sa.select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.time.desc())
        .limit(limit)
    )
    return db.session.scalars(stmt).all()


def daily_notification(logs):
    last_daily = get_last_notification_time('daily')
    if last_daily and last_daily.date() == datetime.utcnow().date():
        return None

    if not logs or should_notify(logs[-1].time, period_days=1):
        return create_notification(
            "Don't forget to do your Check-In logs today!",
            'daily'
        )
    return None


def weekly_notification(logs):
    last_weekly = get_last_notification_time('weekly')
    if last_weekly and not should_notify(last_weekly, period_days=7):
        return None

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    recent = [log for log in logs if week_ago <= log.time <= now]

    if not recent:
        msg = "You haven't logged any emotions last week. Go to Check-In to get started."
    else:
        counts = Counter(log.emotion for log in recent)
        top, cnt = counts.most_common(1)[0]
        msg = (
            f"You logged feeling {top} the most in the last week:\n"
            f"{cnt} out of {len(recent)} entries."
        )

    return create_notification(msg, 'weekly')


def get_notifications(limit: int = 15):
    logs = db.session.scalars(
        sa.select(EmotionLog)
        .where(EmotionLog.user_id == current_user.id)
        .order_by(EmotionLog.time)
    ).all()

    daily_notification(logs)
    weekly_notification(logs)

    last_notifications = get_last_notifications(limit)
    if all(notif.is_read for notif in last_notifications):
        return {'all_read': True, 'notifications': last_notifications}
    return {'all_read': False, 'notifications': last_notifications}


################### SCREENING TOOL ##############################
# List of symptoms
symptom_list = [('1', 'Excessive Worry/Anxiety'), ('2', 'Panic Attack/Intense Fear'),
                ('3', 'Fear/Intense Discomfort in Social Settings'),
                ('4', 'Avoidance of Social Situations'), ('5', 'Low Mood'), ('6', 'No Enjoyment in Anything'),
                ('7', 'Low Energy/Fatigue'),
                ('8', 'Poor Concentration'), ('9', 'Fluctuating Mood'), ('10', 'Incredibly (unusually) Energetic'),
                ('11', 'Intentional Weight Loss (Large Amount)'), ('12', 'Intense Fear of Weight Gain'),
                ('13', 'Very Negative Body Image'),
                ('14', 'Trouble Quitting a Substance'), ('15', 'Physical Self Harm to Oneself')]

# Mapping of symptom id  to condition id
SYMPTOM_TO_CONDITION_MAP = {
    '1': [1],  # ex, Symptom #1 triggers Condition #4
    '2': [2],
    '3': [3],
    '4': [3],
    '5': [4, 10, 11],  # Symptom #5 triggers Condition #4, #10, #11
    '6': [4, 10, 11],
    '7': [4, 10, 11],
    '8': [1, 4, 9],
    '9': [10, 11],
    '10': [10, 11],
    '11': [5, 6, 7],
    '12': [5, 6, 7],
    '13': [5, 6, 7],
    '14': [8],
    '15': [12]
}


# Function to get condition ids from symptoms selected
def selectConditions(selected_symptoms):
    condition_ids = []
    for i in selected_symptoms:
        condition_ids.extend(SYMPTOM_TO_CONDITION_MAP[i])
    conditions = list(dict.fromkeys([id for id in condition_ids]))
    return conditions


# Function to generate list of questions for each condition
def generate_questionnaires(cond_id):
    condition = app.condition_manager.get_condition(cond_id)
    questions = app.condition_manager.get_questions_for_condition(cond_id)

    # Store condition info and questions in the dictionary
    questionnaire = {
        'id': cond_id,
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
    return questionnaire
