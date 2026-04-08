"""
自动化测试平台 - Flask应用工厂
"""
import os
import traceback
from flask import Flask, request
from app.config import config
from app.extensions import init_extensions, db
from app.cli import commands as cli_commands
from app.utils.logger import logger


def create_app(config_name=None):
    """创建Flask应用"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # 生产环境检查
    if config_name == 'production':
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError('生产环境必须设置JWT_SECRET_KEY环境变量')
    
    app.config.from_object(config[config_name])
    
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 初始化日志
    logger.info(f'应用启动，环境: {config_name}')
    
    # 初始化扩展
    init_extensions(app)
    
    # 初始化 Celery
    from app.celery_worker.celery_app import init_celery
    init_celery(app)
    logger.info(f'Celery初始化完成，Redis: {app.config.get("REDIS_URL")}')
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册CLI命令
    register_cli_commands(app)
    
    # 注册请求日志
    register_request_logging(app)
    
    return app


def register_request_logging(app):
    """注册请求日志中间件"""
    @app.before_request
    def log_request():
        if request.path.startswith('/api'):
            logger.debug(f'[{request.method}] {request.path} - {request.remote_addr}')
    
    @app.after_request
    def log_response(response):
        if request.path.startswith('/api'):
            logger.debug(f'[{request.method}] {request.path} - {response.status_code}')
        return response


def register_blueprints(app):
    """注册API蓝图"""
    from app.api.auth import bp as auth_bp
    from app.api.plans import bp as plans_bp
    from app.api.tasks import bp as tasks_bp
    from app.api.suites import bp as suites_bp
    from app.api.cases import bp as cases_bp
    from app.api.dashboard import bp as dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(plans_bp, url_prefix='/api/v1')
    app.register_blueprint(tasks_bp, url_prefix='/api/v1')
    app.register_blueprint(suites_bp, url_prefix='/api/v1')
    app.register_blueprint(cases_bp, url_prefix='/api/v1')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1')


def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f'400错误: {request.path} - {str(error)}')
        return {'success': False, 'message': '请求参数错误', 'code': 400}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f'404错误: {request.path}')
        return {'success': False, 'message': '资源不存在', 'code': 404}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        # 记录详细错误信息
        logger.error(f'500错误: {request.path}')
        logger.error(f'请求方法: {request.method}')
        logger.error(f'请求数据: {request.get_json() if request.is_json else request.data}')
        logger.error(f'错误详情: {str(error)}')
        logger.error(f'堆栈跟踪:\n{traceback.format_exc()}')
        
        # 开发环境返回详细错误
        if app.config.get('DEBUG'):
            return {
                'success': False, 
                'message': f'服务器内部错误: {str(error)}',
                'code': 500,
                'traceback': traceback.format_exc()
            }, 500
        else:
            return {'success': False, 'message': '服务器内部错误', 'code': 500}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """捕获所有未处理的异常"""
        db.session.rollback()
        logger.error(f'未处理异常: {request.path}')
        logger.error(f'错误类型: {type(error).__name__}')
        logger.error(f'错误详情: {str(error)}')
        logger.error(f'堆栈跟踪:\n{traceback.format_exc()}')
        
        if app.config.get('DEBUG'):
            return {
                'success': False,
                'message': f'{type(error).__name__}: {str(error)}',
                'code': 500,
                'traceback': traceback.format_exc()
            }, 500
        else:
            return {'success': False, 'message': '服务器内部错误', 'code': 500}, 500
    
    # 健康检查端点
    @app.route('/')
    def health_check():
        return {'success': True, 'message': '固件自动化测试平台 API 服务运行中', 'version': '1.0.0'}


def register_cli_commands(app):
    """注册CLI命令"""
    for command in cli_commands:
        app.cli.add_command(command)
