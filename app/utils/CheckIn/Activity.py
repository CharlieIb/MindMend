from app.models import Activity
import sqlalchemy as sa

class ActivityManager:
    def __init__(self, session):
        self.session = session
        self.activities = self._load_activities()

    def _load_activities(self):
        '''Loads activities into memory'''
        q = sa.select(Activity)
        return {activ.name: activ.activity_id for activ in self.session.execute(q).scalars().all()}

    def get_activity_id_by_name(self, activity_name):
        '''Gets the activity id by the name'''
        q = sa.select(Activity).where(Activity.name == activity_name)
        return self.session.execute(q).scalar()

