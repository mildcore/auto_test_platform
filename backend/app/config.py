"""
自动化测试平台 - 配置文件
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """基础配置类"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2026'
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # 默认使用SQLite，开发环境
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "data", "auto_test.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2026'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 24小时过期
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Redis配置（Celery消息队列）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery配置
    CELERY_CONFIG = {
        'broker_url': REDIS_URL,
        'result_backend': REDIS_URL,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'Asia/Shanghai',
        'enable_utc': True,
        'task_track_started': True,
        'task_time_limit': 3600,  # 任务超时1小时
        'worker_prefetch_multiplier': 1,  # 公平调度
    }
    
    # 测试引擎配置
    TEST_ENGINE_CONFIG = {
        'max_concurrent': 5,
        'default_timeout': 300,
        'simulation_default_pass_rate': 0.8,
    }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    # 开发环境使用SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "data", "dev.db")}'
    
    # JWT过期时间调长，方便开发调试
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境必须使用环境变量配置数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "data", "prod.db")}'
    
    # JWT密钥从环境变量读取，延迟检查（在应用初始化时）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # SQLAlchemy 连接池配置
    # 从环境变量读取，默认小连接池防止 MySQL 连接数超限
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 5)),
        'max_overflow': int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', 5)),
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 300)),
        'pool_timeout': 30,
    }


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # JWT过期时间调短，方便测试
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
