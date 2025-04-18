import pytest
from app.models import EmotionLog, User
from app.utils.CheckIn.EmotionLog import EmotionLogManager
from datetime import datetime

def test_load_emotional_logs_by_user(session, test_user):
    """Positive test: Load existing emotion logs for a user."""
    log1 = EmotionLog(user_id=test_user.id, emotion='Happy', steps=1000, time=datetime.utcnow())
    log2 = EmotionLog(user_id=test_user.id, emotion='Sad', steps=500, time=datetime.utcnow())
    session.add_all([log1, log2])
    session.commit()

    manager = EmotionLogManager(session, test_user.id)
    logs = manager.emotional_logs # Access the loaded logs directly for verification

    assert len(logs) == 2
    assert log1.log_id in logs
    assert log2.log_id in logs
    assert logs[log1.log_id].emotion == 'Happy'
    assert logs[log2.log_id].emotion == 'Sad'

def test_get_emotion_log_existing(session, test_user):
    """Positive test: Retrieve an existing emotional log by its ID."""
    log = EmotionLog(user_id=test_user.id, emotion='Neutral', steps=700, time=datetime.utcnow())
    session.add(log)
    session.commit()
    session.refresh(log) # Refresh to get the log_id

    manager = EmotionLogManager(session, test_user.id)
    retrieved_log = manager.get_emotion_log(log.log_id)

    assert retrieved_log is not None
    assert retrieved_log.log_id == log.log_id
    assert retrieved_log.emotion == 'Neutral'

def test_get_emotion_log_non_existent(session, test_user):
    """Negative test: Retrieve a non-existent emotional log by its ID."""
    manager = EmotionLogManager(session, test_user.id)
    retrieved_log = manager.get_emotion_log(999) # Assuming 999 is a non-existent ID

    assert retrieved_log is None

def test_add_new_log_mandatory_fields(session, test_user):
    """Positive test: Successfully add a new emotion log with mandatory fields."""
    manager = EmotionLogManager(session, test_user.id)
    initial_log_count = len(manager.emotional_logs)

    manager.add_new_log(emotion='Excited', steps=2000)

    # Verify it's added to the database
    logs_in_db = session.query(EmotionLog).filter_by(user_id=test_user.id).all()
    assert len(logs_in_db) == initial_log_count + 1
    new_log = logs_in_db[-1]
    assert new_log.emotion == 'Excited'
    assert new_log.steps == 2000
    assert new_log.activity_duration is None
    assert new_log.heart_rate is None
    assert new_log.blood_pressure is None
    assert new_log.free_notes is None
    assert new_log.location_id is None
    assert new_log.activity_id is None
    assert new_log.person_id is None

    # Note: The current EmotionLogManager implementation doesn't re-load logs
    # into the in-memory dictionary after adding. You might want to adjust this
    # in your manager class if you need the in-memory list/dict to be live.
    # For this test, we check the database directly.

def test_add_new_log_all_fields(session, test_user, setup_conditions):
    """Positive test: Successfully add a new emotion log with all optional fields."""
    # Create some related entities first
    from app.models import Location, Activity, Person
    location = Location(name='Home')
    activity = Activity(name='Reading')
    person = Person(name='Partner')
    session.add_all([location, activity, person])
    session.commit()
    session.refresh(location)
    session.refresh(activity)
    session.refresh(person)

    manager = EmotionLogManager(session, test_user.id)
    initial_log_count = len(manager.emotional_logs)

    manager.add_new_log(
        emotion='Calm',
        steps=50,
        activity_duration=30,
        heart_rate=65,
        blood_pressure='120/80',
        free_notes='Feeling relaxed after reading.',
        location_id=location.location_id,
        activity_id=activity.activity_id,
        person_id=person.person_id
    )

    # Verify it's added to the database
    logs_in_db = session.query(EmotionLog).filter_by(user_id=test_user.id).all()
    assert len(logs_in_db) == initial_log_count + 1
    new_log = logs_in_db[-1]
    assert new_log.emotion == 'Calm'
    assert new_log.steps == 50
    assert new_log.activity_duration == 30
    assert new_log.heart_rate == 65
    assert new_log.blood_pressure == '120/80'
    assert new_log.free_notes == 'Feeling relaxed after reading.'
    assert new_log.location_id == location.location_id
    assert new_log.activity_id == activity.activity_id
    assert new_log.person_id == person.person_id

def test_delete_log_existing(session, test_user):
    """Positive test: Successfully delete an existing emotional log."""
    log_to_delete = EmotionLog(user_id=test_user.id, emotion='Angry', steps=100, time=datetime.utcnow())
    session.add(log_to_delete)
    session.commit()
    session.refresh(log_to_delete)

    manager = EmotionLogManager(session, test_user.id)
    initial_log_count_in_manager = len(manager.emotional_logs)

    is_deleted = manager.delete_log(log_to_delete.log_id)

    assert is_deleted is True

    # Verify it's removed from the database
    log_in_db = session.query(EmotionLog).get(log_to_delete.log_id)
    assert log_in_db is None

    # Verify it's removed from the in-memory dictionary
    assert log_to_delete.log_id not in manager.emotional_logs
    assert len(manager.emotional_logs) == initial_log_count_in_manager - 1

def test_delete_log_non_existent(session, test_user):
    """Negative test: Attempt to delete a non-existent emotional log."""
    manager = EmotionLogManager(session, test_user.id)
    initial_log_count_in_manager = len(manager.emotional_logs)

    is_deleted = manager.delete_log(999) # Assuming 999 is a non-existent ID

    assert is_deleted is False

    # Verify no logs were deleted from the database (by checking manager's dict size after attempt)
    assert len(manager.emotional_logs) == initial_log_count_in_manager