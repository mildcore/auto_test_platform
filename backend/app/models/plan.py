"""
测试计划模型
"""
from datetime import datetime
from app.extensions import db


class TestPlan(db.Model):
    """测试计划 - 测试策略配置，核心概念"""
    __tablename__ = 'test_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, comment='计划名称，如"v2.1.3 回归测试"')
    description = db.Column(db.Text, comment='计划描述')
    
    # 关联测试套件和用例（JSON数组存储ID列表）
    suite_ids = db.Column(db.JSON, default=list, comment='选中的测试套件ID列表')
    case_ids = db.Column(db.JSON, default=list, comment='选中的测试用例ID列表')
    # 废弃
    case_order = db.Column(db.JSON, default=dict, comment='用例执行顺序配置，格式：{"global": [case_id1, case_id2, ...]}') 
    
    # 执行策略
    trigger_type = db.Column(db.String(32), default='manual', comment='触发方式：manual/schedule/webhook')
    schedule_cron = db.Column(db.String(64), comment='Cron表达式，如"0 2 * * *"（每天2点）')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用（定时任务用）')
    
    # 执行配置
    parallel = db.Column(db.Boolean, default=False, comment='是否并行执行用例')
    max_concurrent = db.Column(db.Integer, default=3, comment='最大并发数')
    
    # 统计信息
    total_runs = db.Column(db.Integer, default=0, comment='总执行次数')
    last_run_at = db.Column(db.DateTime, comment='上次执行时间')
    last_status = db.Column(db.String(32), comment='上次执行状态')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tasks = db.relationship('TestTask', backref='plan', lazy='dynamic', 
                            order_by='TestTask.created_at.desc()')
    
    def __repr__(self):
        return f'<TestPlan {self.name}>'
    
    @property
    def suite_count(self):
        """套件数量"""
        return len(self.suite_ids) if self.suite_ids else 0
    
    @property
    def next_run_at(self):
        """计算下次执行时间"""
        if self.trigger_type != 'schedule' or not self.schedule_cron or not self.is_active:
            return None
        
        try:
            from croniter import croniter
            base_time = self.last_run_at or self.created_at or datetime.utcnow()
            cron = croniter(self.schedule_cron, base_time)
            return cron.get_next(datetime)
        except Exception:
            return None
    
    def to_dict(self, include_stats=False):
        """序列化为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'suite_ids': self.suite_ids,
            'case_ids': self.case_ids,
            'case_order': self.case_order,
            'suite_count': self.suite_count,
            'trigger_type': self.trigger_type,
            'schedule_cron': self.schedule_cron,
            'is_active': self.is_active,
            'parallel': self.parallel,
            'max_concurrent': self.max_concurrent,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }
        
        if include_stats:
            data['total_runs'] = self.total_runs
            data['last_run_at'] = self.last_run_at.isoformat() + 'Z' if self.last_run_at else None
            data['last_status'] = self.last_status
            data['next_run_at'] = self.next_run_at.isoformat() + 'Z' if self.next_run_at else None
        
        return data
