"""
测试任务API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.task_service import TaskService
from app.repositories.task_repo import TaskRepository
from app.utils.response import success, error, paginated

bp = Blueprint('tasks', __name__)
task_service = TaskService()
task_repo = TaskRepository()


@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取测试任务列表，支持搜索和排序"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    plan_id = request.args.get('plan_id', type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 构建查询
    query = task_repo.model.query
    
    if plan_id:
        query = query.filter_by(plan_id=plan_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if keyword:
        query = query.filter(task_repo.model.name.ilike(f'%{keyword}%'))
    
    # 排序
    valid_sort_fields = ['created_at', 'completed_at', 'duration', 'name', 'status']
    if sort_by in valid_sort_fields and hasattr(task_repo.model, sort_by):
        sort_column = getattr(task_repo.model, sort_by)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    else:
        # 默认按创建时间倒序
        query = query.order_by(task_repo.model.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return paginated(
        items=[task.to_dict() for task in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        pages=pagination.pages
    )


@bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """获取测试任务详情"""
    try:
        result = task_service.get_task_status(task_id)
        return success(result)
    except ValueError as e:
        return error(str(e), 404)


@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除测试任务"""
    task = task_repo.get_by_id(task_id)
    if not task:
        return error('测试任务不存在', 404)
    
    try:
        task_repo.delete(task)
        return success(message='删除成功')
    except Exception as e:
        return error(f'删除失败: {str(e)}', 500)


@bp.route('/tasks/<int:task_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    """取消正在执行的任务"""
    try:
        task = task_service.cancel_task(task_id)
        return success(task.to_dict(), '取消成功')
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f'取消失败: {str(e)}', 500)
