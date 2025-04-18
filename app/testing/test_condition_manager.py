import pytest
from app.models import Condition, ConditionQuestion
from app.utils.ScreeningTool.Condition import ConditionManager

def test_load_conditions(session, setup_conditions):
    """Positive test: Load all conditions into memory."""
    manager = ConditionManager(session)
    conditions = manager.conditions

    assert len(conditions) == 3
    assert all(isinstance(c, Condition) for c in conditions.values())
    assert 1 in conditions # Assuming IDs start from 1 or are assigned sequentially
    assert 2 in conditions
    assert 3 in conditions
    assert conditions[1].name == 'Anxiety'
    assert conditions[2].name == 'Depression'
    assert conditions[3].name == 'Stress'

def test_load_questions(session, setup_conditions):
    """Positive test: Load all condition questions into memory."""
    manager = ConditionManager(session)
    questions = manager.questions

    assert len(questions) == 3 # Based on the setup_conditions fixture
    assert all(isinstance(q, ConditionQuestion) for q in questions.values())
    assert (setup_conditions['conditions'][0].cond_id, 1) in questions # Assuming first condition's ID
    assert (setup_conditions['conditions'][0].cond_id, 2) in questions
    assert (setup_conditions['conditions'][1].cond_id, 1) in questions


def test_get_condition_existing(session, setup_conditions):
    """Positive test: Retrieve an existing condition by its ID."""
    manager = ConditionManager(session)
    anxiety_condition = setup_conditions['conditions'][0]
    retrieved_condition = manager.get_condition(anxiety_condition.cond_id)

    assert retrieved_condition is not None
    assert retrieved_condition.cond_id == anxiety_condition.cond_id
    assert retrieved_condition.name == 'Anxiety'

def test_get_condition_non_existent(session, setup_conditions):
    """Negative test: Retrieve a non-existent condition by its ID."""
    manager = ConditionManager(session)
    retrieved_condition = manager.get_condition(999) # Assuming 999 is a non-existent ID

    assert retrieved_condition is None

def test_get_questions_for_condition_with_questions(session, setup_conditions):
    """Positive test: Retrieve questions for a condition that has questions."""
    manager = ConditionManager(session)
    anxiety_condition = setup_conditions['conditions'][0]
    questions_for_anxiety = manager.get_questions_for_condition(anxiety_condition.cond_id)

    assert len(questions_for_anxiety) == 2
    assert all(isinstance(q, ConditionQuestion) for q in questions_for_anxiety)
    assert questions_for_anxiety[0].question == 'Question 1 for Anxiety?'
    assert questions_for_anxiety[1].question == 'Question 2 for Anxiety?'

def test_get_questions_for_condition_without_questions(session, setup_conditions):
    """Positive test: Retrieve questions for a condition that has no questions."""
    manager = ConditionManager(session)
    stress_condition = setup_conditions['conditions'][2] # Stress has no questions in setup
    questions_for_stress = manager.get_questions_for_condition(stress_condition.cond_id)

    assert len(questions_for_stress) == 0

def test_get_questions_for_non_existent_condition(session, setup_conditions):
    """Negative test: Retrieve questions for a non-existent condition."""
    manager = ConditionManager(session)
    questions = manager.get_questions_for_condition(999) # Assuming 999 is a non-existent ID

    assert len(questions) == 0

def test_get_all_conditions(session, setup_conditions):
    """Positive test: Retrieve all conditions."""
    manager = ConditionManager(session)
    all_conditions = manager.get_all_conditions()

    assert len(all_conditions) == 3
    assert all(isinstance(c, Condition) for c in all_conditions)
    # Check if the names are present (order might not be guaranteed)
    condition_names = {c.name for c in all_conditions}
    assert 'Anxiety' in condition_names
    assert 'Depression' in condition_names
    assert 'Stress' in condition_names