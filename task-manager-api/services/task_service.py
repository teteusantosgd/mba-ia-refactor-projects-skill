import logging
from datetime import datetime

from models.task import Task
from shared.clock import utc_now
from shared.constants import (
    DEFAULT_PRIORITY,
    DUE_DATE_FORMAT,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_TASK_STATUSES,
)
from shared.errors import ServiceError

logger = logging.getLogger(__name__)


class TaskService:
    """Regra de negócio de tasks. Recebe seus repositórios por injeção (composition root)."""

    def __init__(self, task_repository, user_repository, category_repository):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def list_tasks(self):
        return self.tasks.get_all_with_relations()

    def get_task(self, task_id):
        task = self.tasks.get_by_id(task_id)
        if not task:
            raise ServiceError("Task não encontrada", 404)
        return task

    def search_tasks(self, query, status, priority, user_id):
        return self.tasks.search(query, status, priority, user_id)

    def create_task(self, data):
        if not data:
            raise ServiceError("Dados inválidos", 400)

        title = data.get("title")
        if not title:
            raise ServiceError("Título é obrigatório", 400)
        self._validate_title_length(title)

        status = data.get("status", "pending")
        self._validate_status(status)

        priority = data.get("priority", DEFAULT_PRIORITY)
        self._validate_priority(priority)

        user_id = data.get("user_id")
        if user_id:
            self._ensure_user_exists(user_id)

        category_id = data.get("category_id")
        if category_id:
            self._ensure_category_exists(category_id)

        task = Task()
        task.title = title
        task.description = data.get("description", "")
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        due_date = data.get("due_date")
        if due_date:
            task.due_date = self._parse_due_date(
                due_date, "Formato de data inválido. Use YYYY-MM-DD"
            )

        tags = data.get("tags")
        if tags:
            task.tags = ",".join(tags) if isinstance(tags, list) else tags

        self._persist_new(task, "Erro ao criar task")
        logger.info("Task criada: %s - %s", task.id, task.title)
        return task

    def update_task(self, task_id, data):
        task = self.get_task(task_id)
        if not data:
            raise ServiceError("Dados inválidos", 400)

        if "title" in data:
            self._validate_title_length(data["title"])
            task.title = data["title"]

        if "description" in data:
            task.description = data["description"]

        if "status" in data:
            self._validate_status(data["status"])
            task.status = data["status"]

        if "priority" in data:
            self._validate_priority(data["priority"])
            task.priority = data["priority"]

        if "user_id" in data:
            if data["user_id"]:
                self._ensure_user_exists(data["user_id"])
            task.user_id = data["user_id"]

        if "category_id" in data:
            if data["category_id"]:
                self._ensure_category_exists(data["category_id"])
            task.category_id = data["category_id"]

        if "due_date" in data:
            if data["due_date"]:
                task.due_date = self._parse_due_date(
                    data["due_date"], "Formato de data inválido"
                )
            else:
                task.due_date = None

        if "tags" in data:
            tags = data["tags"]
            task.tags = ",".join(tags) if isinstance(tags, list) else tags

        task.updated_at = utc_now()
        self._persist("Erro ao atualizar")
        logger.info("Task atualizada: %s", task.id)
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        self.tasks.delete(task)
        self._persist("Erro ao deletar")
        logger.info("Task deletada: %s", task_id)

    def get_stats(self):
        total = self.tasks.count()
        done = self.tasks.count_by_status("done")
        overdue = sum(1 for task in self.tasks.get_all() if task.is_overdue())
        return {
            "total": total,
            "pending": self.tasks.count_by_status("pending"),
            "in_progress": self.tasks.count_by_status("in_progress"),
            "done": done,
            "cancelled": self.tasks.count_by_status("cancelled"),
            "overdue": overdue,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        }

    # --- validações privadas (fonte única, reusada por create e update) ---

    def _validate_title_length(self, title):
        if len(title) < MIN_TITLE_LENGTH:
            raise ServiceError("Título muito curto", 400)
        if len(title) > MAX_TITLE_LENGTH:
            raise ServiceError("Título muito longo", 400)

    def _validate_status(self, status):
        if status not in VALID_TASK_STATUSES:
            raise ServiceError("Status inválido", 400)

    def _validate_priority(self, priority):
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            raise ServiceError("Prioridade deve ser entre 1 e 5", 400)

    def _ensure_user_exists(self, user_id):
        if not self.users.get_by_id(user_id):
            raise ServiceError("Usuário não encontrado", 404)

    def _ensure_category_exists(self, category_id):
        if not self.categories.get_by_id(category_id):
            raise ServiceError("Categoria não encontrada", 404)

    def _parse_due_date(self, value, error_message):
        try:
            return datetime.strptime(value, DUE_DATE_FORMAT)
        except (ValueError, TypeError):
            raise ServiceError(error_message, 400)

    def _persist_new(self, task, error_message):
        try:
            self.tasks.add(task)
            self.tasks.commit()
        except Exception:
            self.tasks.rollback()
            logger.exception("Falha ao persistir task")
            raise ServiceError(error_message, 500)

    def _persist(self, error_message):
        try:
            self.tasks.commit()
        except Exception:
            self.tasks.rollback()
            logger.exception("Falha ao persistir task")
            raise ServiceError(error_message, 500)
