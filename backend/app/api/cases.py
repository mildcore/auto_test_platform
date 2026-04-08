"""
测试用例API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.repositories.case_repo import CaseRepository
from app.utils.response import success, error, paginated

bp = Blueprint('cases', __name__)
case_repo = CaseRepository()


@bp.route('/cases', methods=['GET'])
@jwt_required()
def get_cases():
    """获取测试用例列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    suite_id = request.args.get('suite_id', type=int)
    
    if suite_id:
        items = case_repo.get_by_suite(suite_id)
        return success([c.to_dict() for c in items])
    
    pagination = case_repo.get_all(page=page, per_page=per_page)
    return paginated(
        items=[c.to_dict() for c in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        pages=pagination.pages
    )


@bp.route('/cases/<int:case_id>', methods=['GET'])
@jwt_required()
def get_case(case_id):
    """获取测试用例详情"""
    case = case_repo.get_by_id(case_id)
    if not case:
        return error('测试用例不存在', 404)
    
    return success(case.to_dict(include_script_preview=True))
