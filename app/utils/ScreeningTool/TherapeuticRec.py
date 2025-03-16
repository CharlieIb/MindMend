from app.models import TherapeuticRec, Condition

class TherapeuticRecManager():
    def __init__(self, session):
        self.session = session
        self.recommendations = self._load_recommendations()

    def _load_recommendations(self):
        '''Loads all therapeutic recommedantiosn into meory.'''
        return {rec.rec_id: rec for rec in self.session.query(TherapeuticRec).all()}

    def get_recommendation (self, rec_id):
        '''Retrieves a recommendation by its ID.'''
        return self.recommendations.get(rec_id)

    def get_recommendations_for_condition(self, cond_id):
        '''Retrieves all recommendations for a specific condition'''
        condition = self.session.query(Condition).get(cond_id)
        if condition:
            return condition.therapeutic_recs
        return []