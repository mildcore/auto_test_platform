"""
仪表盘API - 统计数据
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.repositories.plan_repo import PlanRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.suite_repo import SuiteRepository
from app.repositories.case_repo import CaseRepository
from app.utils.response import success

bp = Blueprint('dashboard', __name__)
plan_repo = PlanRepository()
task_repo = TaskRepository()
suite_repo = SuiteRepository()
case_repo = CaseRepository()


@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取仪表盘统计数据"""
    # 统计总数
    total_plans = plan_repo.count()
    total_tasks = task_repo.count()
    total_suites = suite_repo.count()
    total_cases = case_repo.count()
    
    # 运行中任务数
    running_tasks = len(task_repo.get_running_tasks())
    
    # 今日任务数
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    from app.extensions import db
    from app.models import TestTask
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_tasks_query = TestTask.query.filter(
        TestTask.created_at >= today_start,
        TestTask.created_at <= today_end
    )
    today_tasks = today_tasks_query.count()
    
    # 今日通过/失败统计（已完成的任务）
    today_completed = today_tasks_query.filter(
        TestTask.status.in_(['passed', 'failed'])
    ).all()
    today_passed = sum(1 for t in today_completed if t.status == 'passed')
    today_failed = sum(1 for t in today_completed if t.status == 'failed')
    
    # 最近任务状态分布
    from sqlalchemy import func
    status_stats = db.session.query(
        TestTask.status,
        func.count(TestTask.id)
    ).group_by(TestTask.status).all()
    
    return success({
        'total_plans': total_plans,
        'total_tasks': total_tasks,
        'total_suites': total_suites,
        'total_cases': total_cases,
        'running_tasks': running_tasks,
        'today_tasks': today_tasks,
        'today_passed': today_passed,
        'today_failed': today_failed,
        'status_distribution': {status: count for status, count in status_stats}
    })
