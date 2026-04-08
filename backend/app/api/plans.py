"""
测试计划API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.plan_service import PlanService
from app.repositories.plan_repo import PlanRepository
from app.utils.response import success, error, paginated

bp = Blueprint('plans', __name__)
plan_service = PlanService()
plan_repo = PlanRepository()


@bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    """获取测试计划列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = plan_repo.get_all(page=page, per_page=per_page)
    
    return paginated(
        items=[plan.to_dict(include_stats=True) for plan in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        pages=pagination.pages
    )


@bp.route('/plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_plan(plan_id):
    """获取测试计划详情"""
    plan = plan_repo.get_by_id(plan_id)
    if not plan:
        return error('测试计划不存在', 404)
    
    return success(plan.to_dict(include_stats=True))


@bp.route('/plans', methods=['POST'])
@jwt_required()
def create_plan():
    """创建测试计划"""
    data = request.get_json()
    
    if not data:
        return error('请求体不能为空', 400)
    
    if not data.get('name'):
        return error('计划名称不能为空', 400)
    
    if not data.get('suite_ids'):
        return error('必须选择至少一个测试套件', 400)
    
    try:
        plan = plan_service.create(data)
        return success(plan.to_dict(), '创建成功', 201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f'创建失败: {str(e)}', 500)


@bp.route('/plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    """更新测试计划"""
    plan = plan_repo.get_by_id(plan_id)
    if not plan:
        return error('测试计划不存在', 404)
    
    data = request.get_json()
    if not data:
        return error('请求体不能为空', 400)
    
    try:
        updated = plan_repo.update(plan, data)
        return success(updated.to_dict(), '更新成功')
    except Exception as e:
        return error(f'更新失败: {str(e)}', 500)


@bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    """删除测试计划"""
    plan = plan_repo.get_by_id(plan_id)
    if not plan:
        return error('测试计划不存在', 404)
    
    try:
        plan_repo.delete(plan)
        return success(message='删除成功')
    except Exception as e:
        return error(f'删除失败: {str(e)}', 500)


@bp.route('/plans/<int:plan_id>/execute', methods=['POST'])
@jwt_required()
def execute_plan(plan_id):
    """手动执行测试计划"""
    try:
        task = plan_service.execute(plan_id)
        return success(task.to_dict(), '任务已启动')
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f'执行失败: {str(e)}', 500)


@bp.route('/plans/<int:plan_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_plan(plan_id):
    """启用/禁用测试计划"""
    try:
        plan = plan_service.toggle_active(plan_id)
        status = '启用' if plan.is_active else '禁用'
        return success(plan.to_dict(), f'{status}成功')
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(f'操作失败: {str(e)}', 500)


@bp.route('/plans/<int:plan_id>/copy', methods=['POST'])
@jwt_required()
def copy_plan(plan_id):
    """复制测试计划"""
    try:
        new_plan = plan_service.copy_plan(plan_id)
        return success(new_plan.to_dict(), '复制成功')
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(f'复制失败: {str(e)}', 500)
