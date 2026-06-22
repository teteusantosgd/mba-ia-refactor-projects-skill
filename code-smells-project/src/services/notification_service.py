"""Serviço de notificações.

Isola o envio de notificações (e-mail/SMS/push) da regra de negócio. Aqui as
notificações são registradas via logger estruturado; em produção trocaria-se a
implementação por gateways reais sem alterar os serviços que dependem dela.
"""
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def notify_order_created(self, order_id: int, usuario_id: int) -> None:
        logger.info(
            "Notificação de pedido criado enviada",
            extra={"order_id": order_id, "usuario_id": usuario_id},
        )

    def notify_order_status_changed(self, order_id: int, new_status: str) -> None:
        logger.info(
            "Notificação de mudança de status enviada",
            extra={"order_id": order_id, "status": new_status},
        )
