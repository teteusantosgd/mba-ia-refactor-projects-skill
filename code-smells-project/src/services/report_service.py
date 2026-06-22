"""Regra de negócio de relatórios de vendas. Limiares como constantes nomeadas."""
from src.models import OrderRepository

# Faixas de faturamento que liberam desconto e os respectivos percentuais.
REVENUE_TIER_HIGH = 10000
REVENUE_TIER_MEDIUM = 5000
REVENUE_TIER_LOW = 1000
DISCOUNT_RATE_HIGH = 0.10
DISCOUNT_RATE_MEDIUM = 0.05
DISCOUNT_RATE_LOW = 0.02


def _applicable_discount(revenue: float) -> float:
    if revenue > REVENUE_TIER_HIGH:
        return revenue * DISCOUNT_RATE_HIGH
    if revenue > REVENUE_TIER_MEDIUM:
        return revenue * DISCOUNT_RATE_MEDIUM
    if revenue > REVENUE_TIER_LOW:
        return revenue * DISCOUNT_RATE_LOW
    return 0


class ReportService:
    def __init__(self, order_repository: OrderRepository):
        self.orders = order_repository

    def sales_report(self) -> dict:
        total_orders = self.orders.count_all()
        revenue = self.orders.total_revenue()
        discount = _applicable_discount(revenue)

        return {
            "total_pedidos": total_orders,
            "faturamento_bruto": round(revenue, 2),
            "desconto_aplicavel": round(discount, 2),
            "faturamento_liquido": round(revenue - discount, 2),
            "pedidos_pendentes": self.orders.count_by_status("pendente"),
            "pedidos_aprovados": self.orders.count_by_status("aprovado"),
            "pedidos_cancelados": self.orders.count_by_status("cancelado"),
            "ticket_medio": round(revenue / total_orders, 2) if total_orders > 0 else 0,
        }
