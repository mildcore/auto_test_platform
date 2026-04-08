"""
测试套件API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.repositories.suite_repo import SuiteRepository
from app.repositories.case_repo import CaseRepository
from app.utils.response import success, error, paginated

bp = Blueprint('suites', __name__)
suite_repo = SuiteRepository()
case_repo = CaseRepository()


@bp.route('/suites', methods=['GET'])
@jwt_required()
def get_suites():
    """获取测试套件列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    
    if category:
        items = suite_repo.get_by_category(category)
        return success([s.to_dict() for s in items])
    
    pagination = suite_repo.get_all(page=page, per_page=per_page)
    return paginated(
        items=[s.to_dict() for s in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        pages=pagination.pages
    )


@bp.route('/suites', methods=['POST'])
@jwt_required()
def create_suite():
    """创建测试套件"""
    data = request.get_json()
    if not data or not data.get('name'):
        return error('套件名称不能为空', 400)
    
    try:
        suite = suite_repo.create(data)
        return success(suite.to_dict(), '创建成功', 201)
    except Exception as e:
        return error(f'创建失败: {str(e)}', 500)


@bp.route('/suites/<int:suite_id>', methods=['GET'])
@jwt_required()
def get_suite(suite_id):
    """获取测试套件详情（包含用例列表）"""
    suite = suite_repo.get_by_id(suite_id)
    if not suite:
        return error('测试套件不存在', 404)
    
    return success(suite.to_dict(include_cases=True))


@bp.route('/suites/<int:suite_id>/cases', methods=['GET'])
@jwt_required()
def get_suite_cases(suite_id):
    """获取套件下的测试用例列表"""
    suite = suite_repo.get_by_id(suite_id)
    if not suite:
        return error('测试套件不存在', 404)
    
    cases = case_repo.get_by_suite(suite_id)
    return success([c.to_dict() for c in cases])


@bp.route('/suites/<int:suite_id>', methods=['DELETE'])
@jwt_required()
def delete_suite(suite_id):
    """删除测试套件"""
    suite = suite_repo.get_by_id(suite_id)
    if not suite:
        return error('测试套件不存在', 404)
    
    try:
        suite_repo.delete(suite)
        return success(message='删除成功')
    except Exception as e:
        return error(f'删除失败: {str(e)}', 500)


@bp.route('/suites/<int:suite_id>/cases', methods=['POST'])
@jwt_required()
def create_case(suite_id):
    """在套件下创建测试用例"""
    suite = suite_repo.get_by_id(suite_id)
    if not suite:
        return error('测试套件不存在', 404)
    
    data = request.get_json()
    if not data or not data.get('name'):
        return error('用例名称不能为空', 400)
    
    data['suite_id'] = suite_id
    
    try:
        case = case_repo.create(data)
        return success(case.to_dict(), '创建成功', 201)
    except Exception as e:
        return error(f'创建失败: {str(e)}', 500)


@bp.route('/cases/<int:case_id>', methods=['DELETE'])
@jwt_required()
def delete_case(case_id):
    """删除测试用例"""
    case = case_repo.get_by_id(case_id)
    if not case:
        return error('测试用例不存在', 404)
    
    try:
        case_repo.delete(case)
        return success(message='删除成功')
    except Exception as e:
        return error(f'删除失败: {str(e)}', 500)
