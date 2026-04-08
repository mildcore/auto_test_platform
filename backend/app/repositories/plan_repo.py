"""
测试计划Repository
"""
from app.models import TestPlan
from .base import BaseRepository


class PlanRepository(BaseRepository):
    def __init__(self):
        super().__init__(TestPlan)
    
    def get_active_plans(self):
        """获取启用的计划"""
        return self.model.query.filter_by(is_active=True).all()
    
    def get_scheduled_plans(self):
        """获取定时触发的计划"""
        return self.model.query.filter_by(
            is_active=True,
            trigger_type='schedule'
        ).all()
    
    def increment_run_count(self, plan_id):
        """增加执行次数"""
        plan = self.get_by_id(plan_id)
        if plan:
            plan.total_runs += 1
            from app.extensions import db
            db.session.commit()
        return plan
