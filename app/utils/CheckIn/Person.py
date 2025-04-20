from app.models import Person
import sqlalchemy as sa

class PersonManager:
    def __init__(self, session):
        self.session = session
        self.people = self._load_people()

    def _load_people(self):
        '''Loads people into memory'''
        q = sa.select(Person)
        return {people.name: people.person_id for people in self.session.execute(q).scalars().all()}

    def get_person_id_by_name(self, person_name):
        '''Gets the person id by the name'''
        q = sa.select(Person).where(Person.name == person_name)
        return self.session.execute(q).scalar()

