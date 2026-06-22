"""Serializers (DTOs de saída) — contrato de resposta da API, separado dos models de domínio.

Regra de segurança: o hash de senha NUNCA entra na resposta. `serialize_user` omite o campo
`password` de propósito.
"""


def serialize_task(task):
    """Forma base de uma task (POST/PUT/search)."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "user_id": task.user_id,
        "category_id": task.category_id,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "tags": task.tags.split(",") if task.tags else [],
    }


def serialize_task_with_overdue(task):
    """Task individual (GET /tasks/<id>) — inclui o flag de atraso."""
    data = serialize_task(task)
    data["overdue"] = task.is_overdue()
    return data


def serialize_task_with_relations(task):
    """Listagem de tasks (GET /tasks) — inclui atraso e nomes de usuário/categoria."""
    data = serialize_task_with_overdue(task)
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def serialize_task_summary(task):
    """Resumo de task usado em GET /users/<id>/tasks."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }


def serialize_user(user):
    """DTO público de usuário — sem o hash de senha."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
        "created_at": str(user.created_at),
    }


def serialize_category(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "color": category.color,
        "created_at": str(category.created_at),
    }
