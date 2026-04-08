"""
测试套件Repository
"""
from app.models import TestSuite
from .base import BaseRepository


class SuiteRepository(BaseRepository):
    def __init__(self):
        super().__init__(TestSuite)
    
    def get_by_category(self, category):
        """根据分类获取"""
        return self.model.query.filter_by(category=category).all()
