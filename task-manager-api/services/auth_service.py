from shared.errors import ServiceError


class AuthService:
    """Autenticação de usuários."""

    def __init__(self, user_repository, token_service):
        self.users = user_repository
        self.tokens = token_service

    def login(self, data):
        if not data:
            raise ServiceError("Dados inválidos", 400)

        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise ServiceError("Email e senha são obrigatórios", 400)

        user = self.users.get_by_email(email)
        if not user or not user.check_password(password):
            raise ServiceError("Credenciais inválidas", 401)
        if not user.active:
            raise ServiceError("Usuário inativo", 403)

        return user

    def issue_token(self, user):
        return self.tokens.issue_for(user)
