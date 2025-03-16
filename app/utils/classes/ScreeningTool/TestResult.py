from app.models import TestResult
from datetime import datetime


class TestResultManager:
    def __init__(self, session):
        self.session = session

    def add_test_result(self, user_id, cond_id, result):
        '''Add a new test result'''
        test_result = TestResult(
            user_id = user_id,
            cond_id = cond_id,
            result = result,
            timedate = datetime.now()
        )
        self.session.add(test_result)
        self.session.commit()

    def get_test_results_for_user(self, user_id):
        '''Retrieves all test results for a specific user.'''
        return self.session.query(TestResult).filter_by(user_id=user_id).all()

    def get_test_resutls_for_condition(self, cond_id):
        '''Retrieves all test results for a specific condition'''
        return self.session.query(TestResult).filter_by(cond_id=cond_id).all()
