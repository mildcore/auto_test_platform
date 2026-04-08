"""
统一API响应格式
"""
from flask import jsonify


def success(data=None, message="操作成功", code=200):
    """成功响应"""
    response = {
        "success": True,
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response), code


def error(message="操作失败", code=400, errors=None):
    """错误响应"""
    response = {
        "success": False,
        "code": code,
        "message": message,
        "errors": errors
    }
    return jsonify(response), code


def paginated(items, total, page, per_page, pages):
    """分页响应"""
    return success({
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    })
