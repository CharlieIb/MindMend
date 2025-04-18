import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
# Import your app instance and db instance directly
from app import app as flask_app
from app import db as flask_db
from app.models import Base, User, EmotionLog, Condition, ConditionQuestion, UserSettings, Person, Location, Activity # Import all your models

@pytest.fixture(scope='session')
def app():
    """Session-wide test application."""
    # Use the app instance imported from app/__init__.py
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'LOGIN_DISABLED': True # Disable Flask-Login during tests if needed
    })

    # Establish an application context before creating the database
    with flask_app.app_context():
        yield flask_app

# Rest of the fixtures remain largely the same, using the imported flask_app and flask_db

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def engine(app):
    """Session-wide database engine."""
    # Use the app's config directly
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    # Use Base.metadata from your models
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine):
    """Function-wide database session."""
    connection = engine.connect()
    transaction = connection.begin()
    # Use scoped_session for thread-safety if needed, but sessionmaker is usually sufficient for tests
    session = scoped_session(sessionmaker(bind=connection))

    # Bind the session to your Flask-SQLAlchemy db object
    flask_db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()

# Add any other fixtures you might need, like a test user
@pytest.fixture(scope='function')
def test_user(session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password') # Assuming set_password works without app context initially
    session.add(user)
    session.commit()
    # Refresh the user object to get the assigned ID and trigger after_insert listener
    session.refresh(user)
    return user

@pytest.fixture(scope='function')
def setup_conditions(session):
    cond1 = Condition(name='Anxiety', threshold=10)
    cond2 = Condition(name='Depression', threshold=15)
    cond3 = Condition(name='Stress', threshold=5)
    session.add_all([cond1, cond2, cond3])
    session.commit()

    q1_c1 = ConditionQuestion(condition=cond1, q_number=1, question='Question 1 for Anxiety?', value=2)
    q2_c1 = ConditionQuestion(condition=cond1, q_number=2, question='Question 2 for Anxiety?', value=3)
    q1_c2 = ConditionQuestion(condition=cond2, q_number=1, question='Question 1 for Depression?', value=4)
    session.add_all([q1_c1, q2_c1, q1_c2])
    session.commit()

    # Refresh objects to get assigned IDs
    session.refresh(cond1)
    session.refresh(cond2)
    session.refresh(cond3)
    session.refresh(q1_c1)
    session.refresh(q2_c1)
    session.refresh(q1_c2)


    return {
        'conditions': [cond1, cond2, cond3],
        'questions': [q1_c1, q2_c1, q1_c2]
    }