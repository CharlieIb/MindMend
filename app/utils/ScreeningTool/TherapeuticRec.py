from app.models import TherapeuticRec, Condition
import sqlalchemy as sa

class TherapeuticRecManager():
    def __init__(self, session):
        self.session = session
        self.recommendations = self._load_recommendations()

    def _load_recommendations(self):
        '''Loads all therapeutic recommedantiosn into meory.'''
        q = sa.select(TherapeuticRec)
        return {rec.rec_id: rec for rec in self.session.execute(q).scalars().all()}

    def get_recommendation (self, rec_id):
        '''Retrieves a recommendation by its ID.'''
        return self.recommendations.get(rec_id)

    def get_recommendations_for_condition(self, cond_id):
        '''Retrieves all recommendations for a specific condition'''
        condition = self.session.get(Condition, cond_id)
        if condition:
            return condition.therapeutic_recs
        return []