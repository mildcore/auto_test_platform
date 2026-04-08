"""
测试计划服务
"""
from datetime import datetime
from app.repositories.plan_repo import PlanRepository
from app.repositories.task_repo import TaskRepository
from app.extensions import celery
from app.utils.logger import logger
import traceback


class PlanService:
    """测试计划服务"""
    
    def __init__(self):
        self.plan_repo = PlanRepository()
        self.task_repo = TaskRepository()
    
    def create(self, data):
        """创建测试计划"""
        # 验证suite_ids
        suite_ids = data.get('suite_ids', [])
        if not suite_ids:
            raise ValueError('必须选择至少一个测试套件')
        
        logger.info(f'创建测试计划: {data.get("name")}')
        return self.plan_repo.create(data)
    
    def execute(self, plan_id):
        """
        执行测试计划（手动触发）
        
        流程：
        1. 创建测试任务
        2. 提交Celery异步执行
        3. 返回任务信息
        """
        logger.info(f'开始执行测试计划: plan_id={plan_id}')
        
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            logger.error(f'测试计划不存在: plan_id={plan_id}')
            raise ValueError('测试计划不存在')
        
        logger.info(f'计划信息: {plan.name}, suites={plan.suite_ids}, cases={plan.case_ids}')
        
        # 1. 创建任务记录
        task_data = {
            'plan_id': plan_id,
            'name': f"{plan.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'suite_ids': plan.suite_ids,
            'case_ids': plan.case_ids,
            'case_order': plan.case_order,
            'trigger_type': plan.trigger_type,
            'parallel': plan.parallel,
            'max_concurrent': plan.max_concurrent,
            'status': 'pending'
        }
        logger.debug(f'创建任务数据: {task_data}')
        
        try:
            task = self.task_repo.create(task_data)
            logger.info(f'任务创建成功: task_id={task.id}')
        except Exception as e:
            logger.error(f'任务创建失败: {str(e)}')
            logger.error(traceback.format_exc())
            raise
        
        # 2. 提交Celery任务
        try:
            logger.info(f'正在提交 Celery 任务，broker: {celery.conf.get("broker_url")}')
            celery_job = celery.send_task('app.celery_worker.tasks.execute_test_task', args=[task.id])
            logger.info(f'Celery任务提交成功: celery_task_id={celery_job.id}')
        except Exception as e:
            logger.error(f'Celery任务提交失败: {str(e)}')
            logger.error(traceback.format_exc())
            raise
        
        # 3. 更新任务的celery_task_id
        self.task_repo.update_status(
            task.id, 
            'pending',
            celery_task_id=celery_job.id
        )
        
        # 4. 更新计划统计
        self.plan_repo.increment_run_count(plan_id)
        
        return task
    
    def get_scheduled_plans(self):
        """获取需要定时执行的计划"""
        return self.plan_repo.get_scheduled_plans()
    
    def toggle_active(self, plan_id):
        """启用/禁用计划"""
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError('测试计划不存在')
        
        plan.is_active = not plan.is_active
        from app.extensions import db
        db.session.commit()
        
        return plan
    
    def copy_plan(self, plan_id):
        """复制测试计划"""
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError('测试计划不存在')
        
        # 创建新计划数据
        new_plan_data = {
            'name': f"{plan.name}_副本",
            'description': plan.description,
            'suite_ids': plan.suite_ids,
            'case_ids': plan.case_ids,
            'case_order': plan.case_order,
            'trigger_type': plan.trigger_type,
            'schedule_cron': plan.schedule_cron,
            'parallel': plan.parallel,
            'max_concurrent': plan.max_concurrent,
            'is_active': False  # 复制后默认禁用，需要用户手动启用
        }
        
        return self.plan_repo.create(new_plan_data)
