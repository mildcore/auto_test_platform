"""
认证服务
"""
from flask_jwt_extended import create_access_token


class AuthService:
    """认证服务"""
    
    # 简化版：硬编码管理员账号（实际应从数据库查询）
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    def login(self, username, password):
        """用户登录，返回JWT token"""
        if username == self.ADMIN_USERNAME and password == self.ADMIN_PASSWORD:
            token = create_access_token(identity=username)
            return {
                'token': token,
                'username': username
            }
        return None
    
    def get_current_user(self, identity):
        """获取当前用户信息"""
        return {
            'username': identity,
            'role': 'admin'
        }
