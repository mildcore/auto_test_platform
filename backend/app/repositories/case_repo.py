"""
测试用例Repository
"""
from app.models import TestCase
from .base import BaseRepository


class CaseRepository(BaseRepository):
    def __init__(self):
        super().__init__(TestCase)
    
    def get_by_suite(self, suite_id):
        """根据套件ID获取用例"""
        return self.model.query.filter_by(suite_id=suite_id, is_active=True).all()
    
    def get_by_suite_ids(self, suite_ids):
        """根据多个套件ID获取用例"""
        if not suite_ids:
            return []
        return self.model.query.filter(
            self.model.suite_id.in_(suite_ids),
            self.model.is_active == True
        ).all()
    
    def get_by_type(self, test_type):
        """根据测试类型获取"""
        return self.model.query.filter_by(test_type=test_type, is_active=True).all()
