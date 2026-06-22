import logging

from models.category import Category
from shared.constants import DEFAULT_CATEGORY_COLOR
from shared.errors import ServiceError

logger = logging.getLogger(__name__)


class CategoryService:
    """Regra de negócio de categorias."""

    def __init__(self, category_repository, task_repository):
        self.categories = category_repository
        self.tasks = task_repository

    def list_categories(self):
        return self.categories.get_all()

    def task_count(self, category_id):
        return self.tasks.count_by_category(category_id)

    def get_category(self, category_id):
        category = self.categories.get_by_id(category_id)
        if not category:
            raise ServiceError("Categoria não encontrada", 404)
        return category

    def create_category(self, data):
        if not data:
            raise ServiceError("Dados inválidos", 400)

        name = data.get("name")
        if not name:
            raise ServiceError("Nome é obrigatório", 400)

        category = Category()
        category.name = name
        category.description = data.get("description", "")
        category.color = data.get("color", DEFAULT_CATEGORY_COLOR)

        self._persist_new(category, "Erro ao criar categoria")
        return category

    def update_category(self, category_id, data):
        category = self.get_category(category_id)
        if "name" in data:
            category.name = data["name"]
        if "description" in data:
            category.description = data["description"]
        if "color" in data:
            category.color = data["color"]

        self._persist("Erro ao atualizar")
        return category

    def delete_category(self, category_id):
        category = self.get_category(category_id)
        self.categories.delete(category)
        self._persist("Erro ao deletar")

    def _persist_new(self, category, error_message):
        try:
            self.categories.add(category)
            self.categories.commit()
        except Exception:
            self.categories.rollback()
            logger.exception("Falha ao persistir categoria")
            raise ServiceError(error_message, 500)

    def _persist(self, error_message):
        try:
            self.categories.commit()
        except Exception:
            self.categories.rollback()
            logger.exception("Falha ao persistir categoria")
            raise ServiceError(error_message, 500)
