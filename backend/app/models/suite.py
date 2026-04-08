"""
测试套件模型
"""
from datetime import datetime
from app.extensions import db


class TestSuite(db.Model):
    """测试套件 - 测试用例的分类容器"""
    __tablename__ = 'test_suites'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, index=True, comment='套件名称')
    category = db.Column(db.String(64), default='general', index=True, comment='分类:firmware/protocol/performance/power')
    description = db.Column(db.Text, comment='套件描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    cases = db.relationship('TestCase', backref='suite', lazy='dynamic', cascade='all, delete-orphan')
    
    # # 显式定义索引（可以自定义索引名）
    # __table_args__ = (
    #     db.Index('idx_suite_category', 'category'),  
    #     db.Index('idx_suite_name', 'name'),
    # )
    
    def __repr__(self):
        return f'<TestSuite {self.name}>'
    
    def to_dict(self, include_cases=False):
        """序列化为字典
        
        Args:
            include_cases: 是否包含用例列表
        """
        data = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'case_count': self.cases.count(),
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        if include_cases:
            data['cases'] = [case.to_dict() for case in self.cases.all()]
        
        return data
