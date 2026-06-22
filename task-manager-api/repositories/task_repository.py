from sqlalchemy.orm import joinedload

from database import db
from models.task import Task


class TaskRepository:
    """Isola o acesso a dados de Task. Queries sempre via ORM (parametrizadas)."""

    def get_all(self):
        return Task.query.all()

    def get_all_with_relations(self):
        # Eager loading de user/category — evita o N+1 das listagens e relatórios.
        return (
            Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        )

    def get_by_id(self, task_id):
        return db.session.get(Task, task_id)

    def get_by_user(self, user_id):
        return Task.query.filter_by(user_id=user_id).all()

    def search(self, query=None, status=None, priority=None, user_id=None):
        tasks = Task.query
        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f"%{query}%"),
                    Task.description.like(f"%{query}%"),
                )
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))
        return tasks.all()

    def count(self):
        return Task.query.count()

    def count_by_status(self, status):
        return Task.query.filter_by(status=status).count()

    def count_by_category(self, category_id):
        return Task.query.filter_by(category_id=category_id).count()

    def add(self, task):
        db.session.add(task)

    def delete(self, task):
        db.session.delete(task)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
