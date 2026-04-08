"""
Celery应用配置
"""
from celery import Celery
import os

# 尝试从环境变量获取 Redis URL，否则使用默认值
redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# 确保当前目录在 Python 路径中（用于 Worker 启动时导入任务）
import sys
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_dir))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 创建 Celery 实例，包含任务模块
celery = Celery(
    'test_platform',
    broker=redis_url,
    backend=redis_url,
    include=['app.celery_worker.tasks']
)

# 基础配置
celery.conf.task_serializer = 'json'
celery.conf.accept_content = ['json']
celery.conf.result_serializer = 'json'
celery.conf.timezone = 'Asia/Shanghai'
celery.conf.enable_utc = True
celery.conf.task_track_started = True
celery.conf.task_time_limit = 3600
celery.conf.worker_prefetch_multiplier = 1

# Celery Beat 定时任务配置
celery.conf.beat_schedule = {
    'check-scheduled-plans': {
        'task': 'app.celery_worker.tasks.check_scheduled_plans',
        'schedule': 60.0,  # 每分钟检查一次
    },
}
celery.conf.beat_max_loop_interval = 300  # Beat主循环最大间隔5分钟


def init_celery(app):
    """
    初始化Celery配置，绑定Flask应用上下文
    仅在 Flask 应用中使用（非 Worker 启动时）
    """
    # 从 Flask 配置更新（如果配置了的话）
    if 'CELERY_CONFIG' in app.config:
        celery.conf.update(app.config['CELERY_CONFIG'])
    
    # 绑定Flask应用上下文
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
