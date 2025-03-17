from app.models import Location

class LocationManager:
    def __init__(self, session):
        self.session = session
        self.locations = self._load_locations()

    def _load_locations(self):
        '''Loads locations into memory'''
        return {loc.name: loc.location_id for loc in self.session.query(Location).all()}

    def get_activity_id_by_name(self, location_name):
        '''Gets the location id by the name'''
        return self.session.query(Location).filter_by(name=location_name).scalar()

