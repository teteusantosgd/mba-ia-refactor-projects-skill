"""Fábrica de dependências (wiring por requisição).

Monta repositórios e serviços a partir da conexão escopada na requisição atual.
Concentra a injeção de dependência num único lugar, sem estado global mutável.
"""
from src.database import get_connection
from src.models import OrderRepository, ProductRepository, UserRepository
from src.services import (
    NotificationService,
    OrderService,
    ProductService,
    ReportService,
    UserService,
)


def build_product_service() -> ProductService:
    return ProductService(ProductRepository(get_connection()))


def build_user_service() -> UserService:
    return UserService(UserRepository(get_connection()))


def build_order_service() -> OrderService:
    connection = get_connection()
    return OrderService(
        OrderRepository(connection),
        ProductRepository(connection),
        NotificationService(),
    )


def build_report_service() -> ReportService:
    return ReportService(OrderRepository(get_connection()))
