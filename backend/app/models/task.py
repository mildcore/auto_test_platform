"""
测试任务模型
"""
from datetime import datetime
from app.extensions import db


class TestTask(db.Model):
    """测试任务 - 测试计划的一次执行实例"""
    __tablename__ = 'test_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=False, comment='关联的测试计划ID')
    name = db.Column(db.String(256), nullable=False, comment='任务名称（自动生成）')
    
    # 执行状态
    status = db.Column(db.String(32), default='pending', 
                      comment='状态：pending/running/passed/failed/cancelled')
    
    # 执行时间
    started_at = db.Column(db.DateTime, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    
    # 执行配置（从Plan复制，防止Plan修改影响执行中的Task）
    suite_ids = db.Column(db.JSON, default=list, comment='执行的套件ID列表（快照）')
    case_ids = db.Column(db.JSON, default=list, comment='执行的用例ID列表（空表示全选）')
    case_order = db.Column(db.JSON, default=dict, comment='用例执行顺序配置')
    trigger_type = db.Column(db.String(32), default='manual', comment='触发方式：manual/schedule')
    parallel = db.Column(db.Boolean, default=False, comment='是否并行执行')
    max_concurrent = db.Column(db.Integer, default=3, comment='最大并发数')
    
    # 结果统计
    total_cases = db.Column(db.Integer, default=0, comment='总用例数')
    passed_cases = db.Column(db.Integer, default=0, comment='通过数')
    failed_cases = db.Column(db.Integer, default=0, comment='失败数')
    error_cases = db.Column(db.Integer, default=0, comment='错误数')
    
    # 简单报告（JSON格式，包含摘要和执行详情）
    report_json = db.Column(db.JSON, comment='报告内容：{"summary": {...}, "executions": [...]}')
    
    # Celery任务ID（用于查询状态/取消任务）
    celery_task_id = db.Column(db.String(128), comment='Celery任务ID')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TestTask {self.name}>'
    
    @property
    def duration(self):
        """执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def pass_rate(self):
        """通过率"""
        if self.total_cases > 0:
            return round((self.passed_cases / self.total_cases) * 100, 2)
        return 0.0
    
    def to_dict(self, include_report=False):
        """序列化为字典"""
        data = {
            'id': self.id,
            'plan_id': self.plan_id,
            'plan_name': self.plan.name if self.plan else None,
            'name': self.name,
            'status': self.status,
            'trigger_type': self.trigger_type,
            'parallel': self.parallel,
            'max_concurrent': self.max_concurrent,
            'started_at': self.started_at.isoformat() + 'Z' if self.started_at else None,
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None,
            'duration': self.duration,
            'total_cases': self.total_cases,
            'passed_cases': self.passed_cases,
            'failed_cases': self.failed_cases,
            'error_cases': self.error_cases,
            'pass_rate': self.pass_rate,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
        
        if include_report and self.report_json:
            data['report'] = self.report_json
        elif self.report_json:
            data['report_summary'] = self.report_json.get('summary')
        
        return data
