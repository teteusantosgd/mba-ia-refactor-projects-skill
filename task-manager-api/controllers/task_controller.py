from flask import jsonify, request

from container import task_service
from serializers import (
    serialize_task,
    serialize_task_with_overdue,
    serialize_task_with_relations,
)


def get_tasks():
    tasks = task_service.list_tasks()
    return jsonify([serialize_task_with_relations(task) for task in tasks]), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    return jsonify(serialize_task_with_overdue(task)), 200


def create_task():
    task = task_service.create_task(request.get_json())
    return jsonify(serialize_task(task)), 201


def update_task(task_id):
    task = task_service.update_task(task_id, request.get_json())
    return jsonify(serialize_task(task)), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    tasks = task_service.search_tasks(
        request.args.get("q", ""),
        request.args.get("status", ""),
        request.args.get("priority", ""),
        request.args.get("user_id", ""),
    )
    return jsonify([serialize_task(task) for task in tasks]), 200


def task_stats():
    return jsonify(task_service.get_stats()), 200
