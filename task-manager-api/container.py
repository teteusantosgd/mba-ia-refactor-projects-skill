"""Composition root — único lugar onde as dependências são instanciadas e conectadas.

Repositórios → Services (com injeção via construtor). Controllers importam estas instâncias.
"""
from config.settings import settings
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.category_service import CategoryService
from services.notification_service import NotificationService
from services.report_service import ReportService
from services.task_service import TaskService
from services.token_service import TokenService
from services.user_service import UserService

# Repositórios (acesso a dados)
task_repository = TaskRepository()
user_repository = UserRepository()
category_repository = CategoryRepository()

# Services (regra de negócio) — dependências injetadas
notification_service = NotificationService(settings)
task_service = TaskService(task_repository, user_repository, category_repository)
user_service = UserService(user_repository, task_repository)
category_service = CategoryService(category_repository, task_repository)
report_service = ReportService(task_repository, user_repository, category_repository)
token_service = TokenService(settings.SECRET_KEY, settings.JWT_EXPIRATION_SECONDS)
auth_service = AuthService(user_repository, token_service)
