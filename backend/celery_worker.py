"""
Celery Worker 启动入口

使用方法:
    celery -A celery_worker worker --loglevel=info -P solo
    celery -A celery_worker beat --loglevel=info
"""
# 导入 Celery 实例（带有基础配置和任务模块）
from app.celery_worker.celery_app import celery

# 显式导入 tasks 模块，确保 beat_schedule 被加载
from app.celery_worker import tasks

# 导出 celery 供命令行使用
__all__ = ['celery']
