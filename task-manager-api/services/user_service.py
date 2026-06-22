import logging
import re

from models.user import User
from shared.constants import EMAIL_REGEX, MIN_PASSWORD_LENGTH, VALID_USER_ROLES
from shared.errors import ServiceError

logger = logging.getLogger(__name__)


class UserService:
    """Regra de negócio de usuários."""

    def __init__(self, user_repository, task_repository):
        self.users = user_repository
        self.tasks = task_repository

    def list_users(self):
        return self.users.get_all()

    def get_user(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            raise ServiceError("Usuário não encontrado", 404)
        return user

    def get_user_tasks(self, user_id):
        self.get_user(user_id)  # garante 404 se não existir
        return self.tasks.get_by_user(user_id)

    def create_user(self, data):
        if not data:
            raise ServiceError("Dados inválidos", 400)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not name:
            raise ServiceError("Nome é obrigatório", 400)
        if not email:
            raise ServiceError("Email é obrigatório", 400)
        if not password:
            raise ServiceError("Senha é obrigatória", 400)

        self._validate_email(email)
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ServiceError("Senha deve ter no mínimo 4 caracteres", 400)
        if self.users.get_by_email(email):
            raise ServiceError("Email já cadastrado", 409)
        self._validate_role(role)

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        self._persist_new(user, "Erro ao criar usuário")
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return user

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not data:
            raise ServiceError("Dados inválidos", 400)

        if "name" in data:
            user.name = data["name"]

        if "email" in data:
            self._validate_email(data["email"])
            existing = self.users.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise ServiceError("Email já cadastrado", 409)
            user.email = data["email"]

        if "password" in data:
            if len(data["password"]) < MIN_PASSWORD_LENGTH:
                raise ServiceError("Senha muito curta", 400)
            user.set_password(data["password"])

        if "role" in data:
            self._validate_role(data["role"])
            user.role = data["role"]

        if "active" in data:
            user.active = data["active"]

        self._persist("Erro ao atualizar")
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        for task in self.tasks.get_by_user(user_id):
            self.tasks.delete(task)
        self.users.delete(user)
        self._persist("Erro ao deletar")
        logger.info("Usuário deletado: %s", user_id)

    # --- validações privadas ---

    def _validate_email(self, email):
        if not re.match(EMAIL_REGEX, email):
            raise ServiceError("Email inválido", 400)

    def _validate_role(self, role):
        if role not in VALID_USER_ROLES:
            raise ServiceError("Role inválido", 400)

    def _persist_new(self, user, error_message):
        try:
            self.users.add(user)
            self.users.commit()
        except Exception:
            self.users.rollback()
            logger.exception("Falha ao persistir usuário")
            raise ServiceError(error_message, 500)

    def _persist(self, error_message):
        try:
            self.users.commit()
        except Exception:
            self.users.rollback()
            logger.exception("Falha ao persistir usuário")
            raise ServiceError(error_message, 500)
