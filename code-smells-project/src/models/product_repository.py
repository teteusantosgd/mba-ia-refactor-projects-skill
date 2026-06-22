"""Acesso a dados de produtos. SQL parametrizado, sem regra de negócio."""
import sqlite3


def _map_product(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


class ProductRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def find_all(self) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [_map_product(row) for row in cursor.fetchall()]

    def find_by_id(self, product_id: int) -> dict | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        return _map_product(row) if row else None

    def create(self, nome, descricao, preco, estoque, categoria) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update(self, product_id, nome, descricao, preco, estoque, categoria) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, product_id),
        )
        self.connection.commit()

    def delete(self, product_id: int) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        self.connection.commit()

    def search(self, term, categoria=None, min_price=None, max_price=None) -> list[dict]:
        query = "SELECT * FROM produtos WHERE 1 = 1"
        parameters: list = []
        if term:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            like_term = f"%{term}%"
            parameters.extend([like_term, like_term])
        if categoria:
            query += " AND categoria = ?"
            parameters.append(categoria)
        if min_price is not None:
            query += " AND preco >= ?"
            parameters.append(min_price)
        if max_price is not None:
            query += " AND preco <= ?"
            parameters.append(max_price)

        cursor = self.connection.cursor()
        cursor.execute(query, parameters)
        return [_map_product(row) for row in cursor.fetchall()]

    def decrease_stock(self, product_id: int, quantity: int) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantity, product_id),
        )
