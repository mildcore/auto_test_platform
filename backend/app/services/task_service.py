"""
测试任务服务
"""
from celery.result import AsyncResult
from app.repositories.task_repo import TaskRepository
from app.extensions import celery


class TaskService:
    """测试任务服务"""
    
    def __init__(self):
        self.task_repo = TaskRepository()
    
    def get_by_id(self, task_id):
        """获取任务详情"""
        return self.task_repo.get_by_id(task_id)
    
    def get_by_plan(self, plan_id, page=1, per_page=10):
        """获取计划下的任务列表"""
        return self.task_repo.get_by_plan(plan_id, page, per_page)
    
    def cancel_task(self, task_id):
        """
        取消正在执行的任务
        
        注意：只能尝试取消，如果任务已经在执行中，可能无法立即停止
        """
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError('任务不存在')
        
        if task.status not in ['pending', 'running']:
            raise ValueError('只能取消待执行或正在执行的任务')
        
        # 尝试取消Celery任务
        if task.celery_task_id:
            celery.control.revoke(task.celery_task_id, terminate=True)
        
        # 更新任务状态
        self.task_repo.update_status(task_id, 'cancelled')
        
        return task
    
    def get_task_status(self, task_id):
        """获取任务状态（包括Celery状态）"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError('任务不存在')
        
        result = task.to_dict(include_report=(task.status in ['passed', 'failed', 'cancelled']))
        
        # 如果任务正在执行，获取Celery的实时状态
        if task.status == 'running' and task.celery_task_id:
            try:
                celery_result = AsyncResult(task.celery_task_id)
                result['celery_status'] = celery_result.status
                result['celery_info'] = celery_result.info
            except Exception as e:
                # Celery backend 未配置或查询失败，不影响任务详情查看
                result['celery_status'] = 'UNKNOWN'
                result['celery_info'] = str(e)
        
        return result
