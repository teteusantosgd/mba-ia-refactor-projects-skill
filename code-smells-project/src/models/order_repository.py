"""Acesso a dados de pedidos. SQL parametrizado; listagens sem N+1.

As listagens resolvem os itens e o nome do produto em uma única query com JOIN,
agrupando em memória — eliminando o N+1 do código original.
"""
import sqlite3


def _map_order(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": [],
    }


class OrderRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self, usuario_id: int, total: float, items: list[dict]) -> int:
        """Cria o pedido, seus itens e baixa o estoque em uma única transação.

        `items` traz dicts com produto_id, quantidade e preco_unitario já
        resolvidos pela camada de serviço.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        order_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (order_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        self.connection.commit()
        return order_id

    def find_by_user(self, usuario_id: int) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return self._attach_items(cursor.fetchall())

    def find_all(self) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM pedidos")
        return self._attach_items(cursor.fetchall())

    def update_status(self, order_id: int, new_status: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (new_status, order_id),
        )
        self.connection.commit()

    def _attach_items(self, order_rows: list[sqlite3.Row]) -> list[dict]:
        orders = [_map_order(row) for row in order_rows]
        if not orders:
            return orders

        orders_by_id = {order["id"]: order for order in orders}
        placeholders = ",".join("?" for _ in orders_by_id)
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
            "p.nome AS produto_nome "
            "FROM itens_pedido ip "
            "LEFT JOIN produtos p ON p.id = ip.produto_id "
            f"WHERE ip.pedido_id IN ({placeholders})",
            list(orders_by_id.keys()),
        )
        for item in cursor.fetchall():
            orders_by_id[item["pedido_id"]]["itens"].append(
                {
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"] or "Desconhecido",
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
            )
        return orders

    def count_all(self) -> int:
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        return cursor.fetchone()[0]

    def total_revenue(self) -> float:
        cursor = self.connection.cursor()
        cursor.execute("SELECT SUM(total) FROM pedidos")
        return cursor.fetchone()[0] or 0

    def count_by_status(self, status: str) -> int:
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,))
        return cursor.fetchone()[0]
