"""Regra de negócio de pedidos: validação de estoque, cálculo e notificações."""
import logging

from src.models import OrderRepository, ProductRepository
from src.services.notification_service import NotificationService
from src.services.validators import validate_order_status

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        notification_service: NotificationService,
    ):
        self.orders = order_repository
        self.products = product_repository
        self.notifications = notification_service

    def create_order(self, usuario_id: int, itens: list[dict]) -> dict:
        """Retorna {'erro': msg} ou {'pedido_id': id, 'total': total}."""
        total = 0
        resolved_items = []

        for item in itens:
            product = self.products.find_by_id(item["produto_id"])
            if product is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if product["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + product["nome"]}
            total += product["preco"] * item["quantidade"]
            resolved_items.append(
                {
                    "produto_id": item["produto_id"],
                    "quantidade": item["quantidade"],
                    "preco_unitario": product["preco"],
                }
            )

        order_id = self.orders.create(usuario_id, total, resolved_items)
        self.notifications.notify_order_created(order_id, usuario_id)
        return {"pedido_id": order_id, "total": total}

    def list_user_orders(self, usuario_id: int) -> list[dict]:
        return self.orders.find_by_user(usuario_id)

    def list_all_orders(self) -> list[dict]:
        return self.orders.find_all()

    def update_status(self, order_id: int, new_status: str) -> dict:
        """Retorna {'erro': msg} ou {'updated': True}."""
        error = validate_order_status(new_status)
        if error:
            return {"erro": error}

        self.orders.update_status(order_id, new_status)
        self.notifications.notify_order_status_changed(order_id, new_status)
        return {"updated": True}
