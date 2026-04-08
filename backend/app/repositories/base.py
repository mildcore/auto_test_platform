"""
基础Repository类
"""
from app.extensions import db


class BaseRepository:
    """基础Repository，提供通用CRUD操作"""
    
    def __init__(self, model):
        self.model = model
    
    def get_by_id(self, id):
        """根据ID获取"""
        return db.session.get(self.model, id)
    
    def get_all(self, page=1, per_page=10, order_by=None):
        """分页获取所有记录"""
        query = self.model.query
        # 默认按创建时间倒序
        if order_by is None and hasattr(self.model, 'created_at'):
            query = query.order_by(self.model.created_at.desc())
        elif order_by:
            query = query.order_by(order_by)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination
    
    def create(self, data):
        """创建记录"""
        instance = self.model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, instance, data):
        """更新记录"""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, instance):
        """删除记录"""
        db.session.delete(instance)
        db.session.commit()
    
    def count(self):
        """获取总数"""
        return self.model.query.count()
