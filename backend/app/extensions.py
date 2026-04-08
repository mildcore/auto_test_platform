"""
自动化测试平台 - 扩展初始化
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# 初始化扩展（不绑定app，延迟初始化）
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Celery 从 celery_app 导入
from app.celery_worker.celery_app import celery


def init_extensions(app):
    """初始化所有扩展"""
    # 数据库
    db.init_app(app)
    migrate.init_app(app, db)
    
    # JWT认证
    jwt.init_app(app)
    
    # Celery 上下文绑定
    from app.celery_worker.celery_app import init_celery
    init_celery(app)
    
    # 注册JWT回调
    from flask_jwt_extended import create_access_token
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """定义JWT identity格式"""
        return user
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token过期回调"""
        return {'success': False, 'message': '登录已过期，请重新登录', 'code': 401}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Token无效回调"""
        return {'success': False, 'message': '无效的登录凭证', 'code': 401}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少Token回调"""
        return {'success': False, 'message': '请先登录', 'code': 401}, 401
