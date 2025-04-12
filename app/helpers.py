from app import app
from app import db
from app.utils import (ConditionManager, ResourceManager, TherapeuticRecManager, TestResultManager,
                       EmotionLogManager, ActivityManager, LocationManager, PersonManager,
                       HeatMap, TrackHealth, TrackEmotions)
from functools import wraps
from flask import abort, flash
from flask_login import current_user
from datetime import datetime



##################### GENERAL ##################################
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


################ Initializing App ####################
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
                emotion_log_manager = EmotionLogManager(db.session, current_user.id)
            initialized = True
            flash("Application data loaded into memory", "success")

            # Debug/demo code (remove in production)
            _demo_managers(app)

        except Exception as e:
            flash(f"Initialization failed: {str(e)}", "danger")
            raise


def _demo_managers(app):
    """Demo/test function (remove in production)"""
    cond_id = 1

    # Demo condition manager
    condition = app.condition_manager.get_condition(cond_id)
    questions = app.condition_manager.get_questions_for_condition(cond_id)

    # Demo other managers
    recommendations = app.therapeutic_rec_manager.get_recommendations_for_condition(cond_id)
    resources = app.resource_manager.get_resources_for_condition(cond_id)
    user_test_results = app.test_result_manager.get_test_results_for_user(user_id=1)

    print(f"Demo:\n{condition.name}\n{questions}\n{recommendations}\n{resources}\n{user_test_results}")



######################### MindMirror ##################################
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





################### SCREENING TOOL ##############################
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
