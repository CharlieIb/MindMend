from app.models import Location
import sqlalchemy as sa

class LocationManager:
    def __init__(self, session):
        self.session = session
        self.locations = self._load_locations()

    def _load_locations(self):
        '''Loads locations into memory'''
        q = sa.select(Location)
        return {loc.name: loc.location_id for loc in self.session.execute(q).scalars().all()}

    def get_activity_id_by_name(self, location_name):
        '''Gets the location id by the name'''
        q = sa.select(Location).where(Location.name == location_name)
        return self.session.execute(q).scalar()

