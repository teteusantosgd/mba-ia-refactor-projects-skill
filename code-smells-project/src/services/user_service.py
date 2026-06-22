"""Regra de negócio de usuários e autenticação. Senhas sempre com hash forte."""
import logging

from werkzeug.security import check_password_hash, generate_password_hash

from src.models import UserRepository
from src.models.user_repository import _map_user_public

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.users = user_repository

    def list_users(self) -> list[dict]:
        return self.users.find_all()

    def get_user(self, user_id: int) -> dict | None:
        return self.users.find_by_id(user_id)

    def create_user(self, nome: str, email: str, senha: str) -> int:
        password_hash = generate_password_hash(senha)
        user_id = self.users.create(nome, email, password_hash)
        logger.info("Usuário criado", extra={"email": email})
        return user_id

    def authenticate(self, email: str, senha: str) -> dict | None:
        """Retorna o usuário público em caso de sucesso, ou None."""
        row = self.users.find_by_email(email)
        if row and check_password_hash(row["senha"], senha):
            logger.info("Login bem-sucedido", extra={"email": email})
            user = _map_user_public(row)
            # Mantém o contrato original do login (id, nome, email, tipo).
            return {
                "id": user["id"],
                "nome": user["nome"],
                "email": user["email"],
                "tipo": user["tipo"],
            }
        logger.warning("Login falhou", extra={"email": email})
        return None
