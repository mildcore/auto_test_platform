"""
认证API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService
from app.utils.response import success, error

bp = Blueprint('auth', __name__)
auth_service = AuthService()


@bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data:
        return error('请求体不能为空', 400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error('用户名和密码不能为空', 400)
    
    result = auth_service.login(username, password)
    
    if result:
        return success(result, '登录成功')
    else:
        return error('用户名或密码错误', 401)


@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    identity = get_jwt_identity()
    user = auth_service.get_current_user(identity)
    return success(user)
