import pytest
from sqlalchemy import create_engine
from app import app as flask_app, db as flask_db
from app.models import User, EmotionLog, Condition, ConditionQuestion, UserSettings, Person, Location, Activity, TherapeuticRec, Resource, therapeutic_rec_condition, resource_condition


@pytest.fixture(scope='session')
def app():
    """Session-wide test application."""
    # app config for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOGIN_DISABLED': True
        # Add any other test configurations here
    })

    # Push an application context that will be available during the session setup
    with flask_app.app_context():
        yield flask_app


@pytest.fixture(scope='session')
def _db(app):
    """Session-wide test database."""
    # Access the db instance within the app context provided by the 'app' fixture
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

    yield session # Yield the session to the test function

    # Clean up after each test
    session.rollback() # Rollback the nested transaction
    ctx.pop() # Pop the application context


@pytest.fixture(scope='function')
def test_user(session):
    """Function-wide test user fixture, ensures a clean user table."""
    # Ensure users table is empty before creating a new user for this test
    # Use the session provided by the fixture
    session.query(User).delete()
    # Commit the delete to make sure the table is cleared before adding new data
    session.commit()

    user = User(username='testuser', email='test@example.com')
    # Ensure app context is active for operations potentially needing it (like password hashing)
    with flask_app.app_context():
         user.set_password('password')

    session.add(user)
    # Commit the new user. This will trigger the after_insert listener for UserSettings.
    session.commit()

    # Refresh to get the ID assigned by the database and ensure listeners have run
    session.refresh(user)
    return user

@pytest.fixture(scope='function')
def setup_conditions(session):
    """Function-wide fixture to set up conditions and questions, ensures clean tables."""
    # Ensure conditions and condition_questions tables are empty
    # Use the session provided by the fixture
    session.query(ConditionQuestion).delete()
    session.query(Condition).delete()
    # Commit the deletes
    session.commit()

    # Now add the specific data for this fixture
    cond1 = Condition(name='Anxiety', threshold=10)
    cond2 = Condition(name='Depression', threshold=15)
    cond3 = Condition(name='Stress', threshold=5)
    session.add_all([cond1, cond2, cond3])
    # Commit conditions to get their primary keys assigned before adding questions
    session.commit()

    # Refresh conditions to ensure their IDs are loaded into the objects
    session.refresh(cond1)
    session.refresh(cond2)
    session.refresh(cond3)

    # Add questions, linking them by object relationship
    q1_c1 = ConditionQuestion(condition=cond1, q_number=1, question='Question 1 for Anxiety?', value=2)
    q2_c1 = ConditionQuestion(condition=cond1, q_number=2, question='Question 2 for Anxiety?', value=3)
    q1_c2 = ConditionQuestion(condition=cond2, q_number=1, question='Question 1 for Depression?', value=4)
    session.add_all([q1_c1, q2_c1, q1_c2])
    # Commit the questions
    session.commit()

    # Refresh questions if needed, though linking by object should handle IDs
    session.refresh(q1_c1)
    session.refresh(q2_c1)
    session.refresh(q1_c2)

    return {
        'conditions': [cond1, cond2, cond3],
        'questions': [q1_c1, q2_c1, q1_c2]
    }