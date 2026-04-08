"""
测试任务Repository
"""
from app.models import TestTask
from .base import BaseRepository


class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(TestTask)
    
    def get_by_plan(self, plan_id, page=1, per_page=10):
        """根据计划ID获取任务"""
        return self.model.query.filter_by(plan_id=plan_id)\
            .order_by(self.model.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    def get_running_tasks(self):
        """获取正在执行的任务"""
        return self.model.query.filter_by(status='running').all()
    
    def update_status(self, task_id, status, **kwargs):
        """更新任务状态"""
        task = self.get_by_id(task_id)
        if task:
            task.status = status
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            from app.extensions import db
            db.session.commit()
        return task
