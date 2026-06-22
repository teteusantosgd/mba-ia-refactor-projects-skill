from flask import jsonify, request

from container import category_service
from serializers import serialize_category


def get_categories():
    categories = category_service.list_categories()
    result = []
    for category in categories:
        data = serialize_category(category)
        data["task_count"] = category_service.task_count(category.id)
        result.append(data)
    return jsonify(result), 200


def create_category():
    category = category_service.create_category(request.get_json())
    return jsonify(serialize_category(category)), 201


def update_category(cat_id):
    category = category_service.update_category(cat_id, request.get_json())
    return jsonify(serialize_category(category)), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({"message": "Categoria deletada"}), 200
