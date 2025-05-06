from app.models import TestResult
from datetime import datetime
import sqlalchemy as sa


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
        q = sa.select(TestResult).where(TestResult.user_id == user_id)
        return self.session.execute(q).scalars().all()

    def get_test_resutls_for_condition(self, cond_id):
        '''Retrieves all test results for a specific condition'''
        q = sa.select(TestResult).where(TestResult.cond_id == cond_id)
        return self.session.execute(q).scalars().all()
