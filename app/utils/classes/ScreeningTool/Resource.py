from app.models import Resource, Condition

class ResourceManager:
    def __init__(self, session):
        self.session = session
        self.resources = self._load_resources()

    def _load_resources(self):
        '''Loads all resources into memory'''
        return {res.resource_id: res for res in self.session.query(Resource).all()}

    def get_resource(self, resource_id):
        '''Retrieves a resource by its ID'''
        return self.resources.get(resource_id)

    def get_resources_for_condition(self, cond_id):
        '''Retrieves all the resources for a specific condition by its ID'''
        condition = self.session.query(Condition).get(cond_id)
        if condition:
            return condition.resources
        return []

