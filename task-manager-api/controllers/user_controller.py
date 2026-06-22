from flask import jsonify, request

from container import user_service
from serializers import serialize_task, serialize_task_summary, serialize_user


def get_users():
    users = user_service.list_users()
    result = []
    for user in users:
        data = serialize_user(user)
        data["task_count"] = len(user.tasks)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = user_service.get_user(user_id)
    data = serialize_user(user)
    data["tasks"] = [serialize_task(task) for task in user_service.get_user_tasks(user_id)]
    return jsonify(data), 200


def create_user():
    user = user_service.create_user(request.get_json())
    return jsonify(serialize_user(user)), 201


def update_user(user_id):
    user = user_service.update_user(user_id, request.get_json())
    return jsonify(serialize_user(user)), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    tasks = user_service.get_user_tasks(user_id)
    return jsonify([serialize_task_summary(task) for task in tasks]), 200
