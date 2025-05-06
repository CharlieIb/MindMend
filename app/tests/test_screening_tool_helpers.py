import pytest
from app import app as flask_app
from app.utils.DatabaseAccess.ScreeningTool import ConditionManager
from app.utils.General.helpers import selectConditions, generate_questionnaires
from app.models import Condition, ConditionQuestion

@pytest.fixture(autouse=True)
def init_screening_tool_manager(session):
    # Attaches ConditionManager to the flask app so app.condition_manager
    # can be called by generate_questionnaires()
    flask_app.condition_manager = ConditionManager(session)
    yield
    # Cleans up once the test is finished
    del flask_app.condition_manager

@pytest.fixture
def fake_conditions_and_questions(session):
    # Sets up 2 example conditions with associated thresholds and
    # with 3 questions

    # Clear out any existing rows
    session.query(ConditionQuestion).delete()
    session.query(Condition).delete()
    session.commit()

    # Create two conditions
    c1 = Condition(name='A', threshold=5)
    c2 = Condition(name='B', threshold=3)
    session.add_all([c1, c2])
    session.commit()
    session.refresh(c1); session.refresh(c2)

    # Add questions: two for c1, one for c2
    q1 = ConditionQuestion(cond_id=c1.cond_id, q_number=1,
                           question='Q1 for A', value=2)
    q2 = ConditionQuestion(cond_id=c1.cond_id, q_number=2,
                           question='Q2 for A', value=3)
    q3 = ConditionQuestion(cond_id=c2.cond_id, q_number=1,
                           question='Q1 for B', value=1)
    session.add_all([q1, q2, q3])
    session.commit()

    return {'conditions': {c1.cond_id: c1, c2.cond_id: c2}}

def test_select_conditions_deduplicates_and_orders():
    # when selectConditions is give a list of symptom IDs
    # it should map each symptom to its assigned condition(s)
    # it should also flatten and dedupe the list while preserving the order

    # We know SYMPTOM_TO_CONDITION_MAP maps:
    # '1' → [1,2], '2' → [2], '3' → [3]
    selected = ['1', '2', '1']
    result = selectConditions(selected)
    # You should see [1,2] exactly once each, in the order of encounter
    assert result == [1, 2]

def test_generate_questionnaires_returns_complete_structure(
        session, fake_conditions_and_questions):
    # the generate_questionnaires must return a dictionary with the following keys:
    # id, name, threshold, questions

    # chooses one of the fake conditions
    cond_id = next(iter(fake_conditions_and_questions['conditions']))
    payload = generate_questionnaires(cond_id)

    # Check keys and types
    assert set(payload.keys()) == {'id', 'name', 'threshold', 'questions'}
    assert payload['id'] == cond_id
    assert isinstance(payload['name'], str)
    assert isinstance(payload['threshold'], int)

    qs = payload['questions']
    # The number of returned questions must also match the rows in the database
    actual_count = session.query(ConditionQuestion)\
                          .filter_by(cond_id=cond_id).count()
    assert len(qs) == actual_count

    # Each question entry must have: q_number, question, and value
    for entry in qs:
        assert set(entry.keys()) == {'q_number', 'question', 'value'}
        assert isinstance(entry['q_number'], int)
        assert isinstance(entry['question'], str)
        assert isinstance(entry['value'], int)
