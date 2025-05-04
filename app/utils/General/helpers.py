from app import app
from app import db
from app.utils import (ConditionManager, ResourceManager, TherapeuticRecManager, TestResultManager, EmotionLogManager,
                       HeatMap, TrackHealth)
from functools import wraps
from flask import abort, flash
from flask_login import current_user
from datetime import datetime
from typing import Any, Dict, List, Tuple


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
def get_heatmap_info() -> Dict[str, Any]:
    """
    Gather all necessary heatmap data for the current user and date.

    Returns:
        A dictionary containing:
        - 'curr_day', 'curr_month', 'curr_year': current date integers.
        - 'month': month layout from HeatMap.month_display().
        - 'year': year layout from HeatMap.year_display().
        - 'months': list of month names January–December.
    """
    now = datetime.now()
    curr_day, curr_month, curr_year = now.day, now.month, now.year

    data_log: List[Dict[str, Any]] = [
        {'date': log.time, 'emotion': log.emotion}
        for log in current_user.emotion_logs
    ]

    heatmap = HeatMap(curr_day, curr_month, curr_year, data_log)
    month_layout: List[Any] = heatmap.month_display()
    year_layout: List[Any] = heatmap.year_display()

    months: List[str] = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    return {
        'curr_day': curr_day,
        'curr_month': curr_month,
        'curr_year': curr_year,
        'month': month_layout,
        'year': year_layout,
        'months': months
    }


def get_health_info() -> Dict[str, Any]:
    """
    Collect health metrics and computed analytics for the current user.

    Returns:
        A dictionary containing:
        - Raw inputs: 'steps', 'activity_duration', 'heart_rate', 'age'.
        - Goals: 'steps_goal', 'activity_duration_goal'.
        - Percentages: 'steps_percentage_complete', 'activity_percentage_complete'.
        - Heart-rate stats: 'max_heart_rate', 'min_heart_rate', 'avg_heart_rate'.
        - Scaled heart-rate info: 'heart_rate_range', 'heart_zones', 'heart_zones_scaled'.
    """
    # Sample data—replace with real queries
    steps: int = 6908
    activity_duration: int = 110
    heart_rate: List[int] = [50, 64, 153]

    tracker = TrackHealth(
        steps=steps,
        activity_duration=activity_duration,
        heart_rate=heart_rate
    )

    return {
        'steps': steps,
        'steps_goal': tracker.steps_goal,
        'steps_percentage_complete': tracker.steps_percentage_complete(),
        'activity_duration': activity_duration,
        'activity_duration_goal': tracker.activity_duration_goal,
        'activity_percentage_complete': tracker.activity_percentage_complete(),
        'heart_rate': heart_rate,
        'max_heart_rate': tracker.max_heart_rate(),
        'min_heart_rate': tracker.min_heart_rate(),
        'avg_heart_rate': tracker.avg_heart_rate(),
        'heart_rate_range': tracker.heart_rate_range(),
        'heart_zones': tracker.heart_rate_zones(),
        'heart_zones_scaled': tracker.heart_rate_zone_progress_bar(),
        'age': tracker.age
    }


def get_emotions_info_from_logs(logs: List[Any]) -> Dict[str, Any]:
    """
    Summarise emotion logs into counts, percentages and chart segments.

    Args:
        logs: Iterable of log objects with .emotion attribute.

    Returns:
        A dictionary containing:
        - 'emotions': counts per emotion.
        - 'total_emotion_logs': total number of logs.
        - 'emotions_percentage': half-scaled percentage per emotion (0–50).
        - 'segments': list of dicts with 'emotion', 'value', 'cumulative' (0–50 scale) for charting.
        - 'max_num': [top_emotion, raw_count]
    """
    default_emotions: Dict[str, int] = {
        'Anger': 0, 'Anxious': 0, 'Sad': 0,
        'Happy': 0, 'Love': 0, 'Calm': 0
    }

    try:
        emotions = default_emotions.copy()
        for log in logs:
            emotions[log.emotion] = emotions.get(log.emotion, 0) + 1

        total = sum(emotions.values())
        if total > 0:
            # percentages on 0–100, then halved to 0–50
            emotions_percentage = {
                emo: round(count / total * 50)
                for emo, count in emotions.items()
            }
            # find top emotion
            top_emotion, top_val = max(emotions.items(), key=lambda x: x[1])
            max_num = [top_emotion, top_val]

            segments: List[Dict[str, Any]] = []
            cumulative = 0
            for i, (emo, val) in enumerate(emotions_percentage.items()):
                cumulative = min(50, cumulative + val)
                if i == len(emotions_percentage) - 1:
                    cumulative = 50
                segments.append({
                    'emotion': emo,
                    'value': val,
                    'cumulative': cumulative
                })
        else:
            emotions_percentage = default_emotions.copy()
            segments = [
                {'emotion': emo, 'value': 0, 'cumulative': -1}
                for emo in default_emotions
            ]
            max_num = [None, 0]

        return {
            'emotions': emotions,
            'total_emotion_logs': total,
            'emotions_percentage': emotions_percentage,
            'segments': segments,
            'max_num': max_num
        }

    except Exception as e:
        # fallback on error
        print(f"Error: {e}")
        return {
            'emotions': default_emotions.copy(),
            'total_emotion_logs': 0,
            'emotions_percentage': default_emotions.copy(),
            'segments': [
                {'emotion': emo, 'value': 0, 'cumulative': 0}
                for emo in default_emotions
            ],
            'max_num': [None, 0]
        }


def get_emotions_info() -> Dict[str, Any]:
    """
    Retrieve emotion summary for the current user.

    Returns:
        The same structure as get_emotions_info_from_logs.
    """
    return get_emotions_info_from_logs(current_user.emotion_logs)


################### SCREENING TOOL ##############################
# List of symptoms
# The tuple’s first element (string ID) is what the form POSTs;
# the second element is what the user sees in the multi-select UI.
symptom_list = [('1', 'Excessive Worry/Anxiety'), ('2', 'Panic Attack/Intense Fear'),
                ('3', 'Fear/Intense Discomfort in Social Settings'),
                ('4', 'Avoidance of Social Situations'), ('5', 'Low Mood'), ('6', 'No Enjoyment in Anything'),
                ('7', 'Low Energy/Fatigue'),
                ('8', 'Poor Concentration'), ('9', 'Fluctuating Mood'), ('10', 'Incredibly (unusually) Energetic'),
                ('11', 'Intentional Weight Loss (Large Amount)'), ('12', 'Intense Fear of Weight Gain'),
                ('13', 'Very Negative Body Image'),
                ('14', 'Trouble Quitting a Substance'), ('15', 'Physical Self Harm to Oneself')]

# Mapping of symptom id  to condition id
#  This table is the source that links each front-end
#   symptom choice to one-or-more condition IDs stored in the database.
SYMPTOM_TO_CONDITION_MAP = {
    '1': [1],      # “Excessive Worry”  →  Generalised Anxiety (cond_id 1)
    '2': [2],
    '3': [3],
    '4': [3],      # two symptoms map to Social Anxiety (3)
    '5': [4, 10],  # low mood may flag Depression or Bipolar types
    '6': [4, 10],
    '7': [4, 10],
    '8': [1, 4, 9], # poor concentration overlaps Anxiety/Depression/ADHD
    '9': [10],
    '10': [10],
    '11': [5, 6, 7],
    '12': [5, 6, 7],
    '13': [5, 6, 7],
    '14': [8],
    '15': [11]
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
