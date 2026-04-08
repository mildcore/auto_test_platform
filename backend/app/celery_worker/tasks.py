"""
Celery任务定义
"""
import time
import traceback
from datetime import datetime
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from app.utils.logger import logger


@shared_task(bind=True, max_retries=3)
def execute_test_task(self, task_id):
    """
    执行测试任务（Celery任务）
    """
    from app import create_app
    from app.repositories.task_repo import TaskRepository
    from app.services.executor import TestExecutor
    from app.extensions import db
    
    app = create_app()
    
    with app.app_context():
        task_repo = TaskRepository()
        executor = TestExecutor()
        
        task = task_repo.get_by_id(task_id)
        if not task:
            logger.error(f'任务不存在: task_id={task_id}')
            return {'error': 'Task not found'}
        
        logger.info(f'开始执行任务: task_id={task_id}, name={task.name}')
        logger.info(f'执行配置: suites={task.suite_ids}, cases={task.case_ids}, parallel={task.parallel}')
        
        try:
            # 更新状态为running
            task_repo.update_status(
                task_id,
                'running',
                started_at=datetime.utcnow()
            )
            logger.info(f'任务状态更新为 running')
            
            # 上报任务已开始
            self.update_state(state='PROGRESS', meta={'status': '开始执行测试用例'})
            
            # 执行测试 - 传递 app_context 给并行执行使用
            logger.info(f'调用执行器...')
            result = executor.run(task, app_context=app.app_context)
            logger.info(f'执行完成: {result}')
            
            # 更新任务完成状态
            task_repo.update_status(
                task_id,
                result['status'],  # passed/failed
                completed_at=datetime.utcnow(),
                total_cases=result['total'],
                passed_cases=result['passed'],
                failed_cases=result['failed'],
                error_cases=result['error'],
                report_json=result['report']
            )
            logger.info(f'任务状态更新完成: status={result["status"]}')
            
            # 更新计划的last_run信息
            try:
                from app.repositories.plan_repo import PlanRepository
                plan_repo = PlanRepository()
                plan = plan_repo.get_by_id(task.plan_id)
                if plan:
                    plan.last_run_at = datetime.utcnow()
                    plan.last_status = result['status']
                    db.session.commit()
                    logger.info(f'计划统计更新完成: plan_id={task.plan_id}')
            except Exception as e:
                logger.error(f'更新计划统计失败: {e}')
            
            return result
            
        except SoftTimeLimitExceeded:
            logger.error(f'任务执行超时: task_id={task_id}')
            task_repo.update_status(
                task_id,
                'failed',
                completed_at=datetime.utcnow()
            )
            raise
            
        except Exception as exc:
            logger.error(f'任务执行异常: task_id={task_id}, error={exc}')
            logger.error(traceback.format_exc())
            task_repo.update_status(
                task_id,
                'failed',
                completed_at=datetime.utcnow()
            )
            # 重试逻辑
            raise self.retry(exc=exc, countdown=60)


@shared_task
def check_scheduled_plans():
    """
    定时检查并执行计划（Celery Beat调度）
    每分钟执行一次，检查是否有定时计划需要执行
    """
    from app import create_app
    from app.services.plan_service import PlanService
    from croniter import croniter
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        plan_service = PlanService()
        plans = plan_service.get_scheduled_plans()
        
        executed_count = 0
        now = datetime.utcnow()
        
        for plan in plans:
            if not plan.schedule_cron:
                continue
            
            try:
                # 基于上次执行时间或计划创建时间计算下次执行时间
                base_time = plan.last_run_at or plan.created_at
                if not base_time:
                    base_time = now
                    
                itr = croniter(plan.schedule_cron, base_time)
                next_run = itr.get_next(datetime)
                
                # 如果下次执行时间已经过了，就执行计划
                # 允许1分钟的误差窗口（因为beat每分钟检查一次）
                if next_run <= now:
                    logger.info(f"定时执行计划: {plan.name} (id={plan.id}), cron={plan.schedule_cron}")
                    plan_service.execute(plan.id)
                    executed_count += 1
            except Exception as e:
                logger.error(f"检查计划 {plan.id} 失败: {e}")
        
        if executed_count > 0:
            logger.info(f"定时检查完成: 检查了 {len(plans)} 个计划，执行了 {executed_count} 个")
        
        return {'checked': len(plans), 'executed': executed_count}
