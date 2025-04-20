from app.models import Activity

class ActivityManager:
    def __init__(self, session):
        self.session = session
        self.activities = self._load_activities()

    def _load_activities(self):
        '''Loads activities into memory'''
        return {activ.name: activ.activity_id for activ in self.session.query(Activity).all()}

    def get_activity_id_by_name(self, activity_name):
        '''Gets the activity id by the name'''
        return self.session.query(Activity.activity_id).filter_by(name=activity_name).scalar()

