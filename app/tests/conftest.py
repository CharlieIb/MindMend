import pytest
from sqlalchemy import create_engine, delete
from app import app as flask_app, db as flask_db
from app.models import User, EmotionLog, Condition, ConditionQuestion, UserSettings, Person, Location, Activity, TherapeuticRec, Resource, therapeutic_rec_condition, resource_condition
from datetime import datetime


@pytest.fixture(scope='session')
def app():
    """Session-wide test application."""
    # app config for tests
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOGIN_DISABLED': True
        # ADD ANY OTHER TEST CONFIGURATION NEEDED HERE!
    })

    # Yield the application context that will be available during the session setup
    # with will handle the teardown of the app context
    with flask_app.app_context():
        yield flask_app


@pytest.fixture(scope='session')
def _db(app):
    """Session-wide test database."""
    # Access the db instance within the app context provided by this test 'app' fixture
    with app.app_context():

        flask_db.create_all()
        yield flask_db
        flask_db.drop_all()


@pytest.fixture(scope='function')
def session(_db, app):
    """Function-wide database session with transaction rollback."""
    # Ensure app context is pushed for this function's scope
    ctx = app.app_context()
    ctx.push()

    # Get the database session managed by Flask-SQLAlchemy
    # This session is tied to the engine created in the _db fixture
    session = _db.session

    # Use nested transaction to achieve per-test isolation
    session.begin_nested()

    # Yield the session to the test function
    yield session

    # This runs after each test
    # Clean up
    session.rollback() # Rollback the nested transaction
    ctx.pop() # Pop the application context


@pytest.fixture(scope='function')
def test_user(session):
    """Function-wide test user fixture, ensures a clean user table."""
    # Ensure users table is empty before creating a new user for this test
    # use the session fixture

    session.execute(delete(User))
    session.commit()

    user = User(username='testuser', email='test@example.com')
    # Ensure app context is active for password hashing
    with flask_app.app_context():
         user.set_password('password')

    session.add(user)

    session.commit()

    # Refresh to ensure IDs are loaded in the db, and ensure listeners have run
    session.refresh(user)
    return user

@pytest.fixture(scope='function')
def setup_conditions(session):
    """Function-wide fixture to set up conditions and questions, ensures clean tables and smooth tests."""

    # Ensure conditions and condition_questions tables are empty
    # use the session fixture

    session.execute(delete(ConditionQuestion))
    session.execute(delete(Condition))
    session.commit()

    # Now add the specific data for this fixture
    cond1 = Condition(name='Anxiety', threshold=10)
    cond2 = Condition(name='Depression', threshold=15)
    cond3 = Condition(name='Stress', threshold=5)
    session.add_all([cond1, cond2, cond3])

    session.commit()

    # Refresh conditions to ensure IDs are loaded into the objects
    session.refresh(cond1)
    session.refresh(cond2)
    session.refresh(cond3)

    # Add questions, linking them by object relationship
    q1_c1 = ConditionQuestion(condition=cond1, q_number=1, question='Question 1 for Anxiety?', value=7)
    q2_c1 = ConditionQuestion(condition=cond1, q_number=2, question='Question 2 for Anxiety?', value=3)
    q1_c2 = ConditionQuestion(condition=cond2, q_number=1, question='Question 1 for Depression?', value=4)
    session.add_all([q1_c1, q2_c1, q1_c2])

    session.commit()

    # Refresh questions to ensure IDs are loaded into the objects
    session.refresh(q1_c1)
    session.refresh(q2_c1)
    session.refresh(q1_c2)

    return {
        'conditions': [cond1, cond2, cond3],
        'questions': [q1_c1, q2_c1, q1_c2]
    }

@pytest.fixture
def client(app):
    """Simulates HTTP requests."""
    return app.test_client()

@pytest.fixture
def logged_in_user(client, session, test_user):
    """Mocks a logged-in user."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    return test_user