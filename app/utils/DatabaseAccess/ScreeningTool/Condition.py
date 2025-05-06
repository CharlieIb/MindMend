from app.models import Condition, ConditionQuestion
import sqlalchemy as sa

class ConditionManager():
    def __init__(self, session):
        self.session = session
        self.conditions = self._load_conditions()
        self.questions = self._load_questions()


    def _load_conditions(self):
        """Loads all conditions into memory """
        q = sa.select(Condition)
        return {cond.cond_id: cond for cond in self.session.execute(q).scalars().all()}

    def _load_questions(self):
        """Loads all condition questions into memory """
        query = sa.select(ConditionQuestion)
        return {(q.cond_id, q.q_number): q for q in self.session.execute(query).scalars().all()}

    def get_condition(self, cond_id):
        '''Retrieves a condition by its ID'''
        return self.conditions.get(cond_id)

    def get_questions_for_condition(self, cond_id):
        '''Retrieves all the questions for a specific condition.'''
        return [q for (cid, _), q in self.questions.items() if cid == cond_id]

    def get_all_conditions(self):
        '''Retrieves all conditions'''
        return list(self.conditions.values())


