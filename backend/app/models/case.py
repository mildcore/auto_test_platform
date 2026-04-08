"""
测试用例模型
"""
from datetime import datetime
from app.extensions import db


class TestCase(db.Model):
    """测试用例 - 单个测试定义"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=False, comment='所属套件ID')
    
    # 基本信息
    name = db.Column(db.String(256), nullable=False, comment='用例名称')
    description = db.Column(db.Text, comment='用例描述')
    test_type = db.Column(db.String(64), default='unit', comment='测试类型：unit/integration/system/performance')
    
    # 【预留】真实测试脚本（演示说明用，实际执行仍模拟）
    script_content = db.Column(db.Text, comment='测试脚本内容（Python代码）')
    script_type = db.Column(db.String(32), default='pytest', comment='脚本类型：pytest/unittest/custom')
    
    # 执行配置
    timeout = db.Column(db.Integer, default=300, comment='超时时间（秒）')
    priority = db.Column(db.Integer, default=2, comment='优先级 1-4')
    
    # 模拟执行配置（实际使用）
    simulation_pass_rate = db.Column(db.Float, default=0.8, comment='模拟通过率（0-1）')
    
    # 状态
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TestCase {self.name}>'
    
    def to_dict(self, include_script_preview=False):
        """序列化为字典"""
        data = {
            'id': self.id,
            'suite_id': self.suite_id,
            'suite_name': self.suite.name if self.suite else None,
            'name': self.name,
            'description': self.description,
            'test_type': self.test_type,
            'script_type': self.script_type,
            'timeout': self.timeout,
            'priority': self.priority,
            'simulation_pass_rate': self.simulation_pass_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        # 脚本预览（仅前200字符）
        if include_script_preview and self.script_content:
            data['script_preview'] = self.script_content[:200] + '...' if len(self.script_content) > 200 else self.script_content
        
        return data
