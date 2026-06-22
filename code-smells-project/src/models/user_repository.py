"""Acesso a dados de usuários. SQL parametrizado, sem regra de negócio.

O hash da senha nunca é exposto: o mapeamento público omite o campo `senha`.
"""
import sqlite3


def _map_user_public(row: sqlite3.Row) -> dict:
    """Mapeia o usuário para resposta da API, sem o campo sensível `senha`."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


class UserRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def find_all(self) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [_map_user_public(row) for row in cursor.fetchall()]

    def find_by_id(self, user_id: int) -> dict | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return _map_user_public(row) if row else None

    def find_by_email(self, email: str) -> sqlite3.Row | None:
        """Retorna a linha completa (inclui hash) para verificação de senha."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()

    def create(self, nome, email, password_hash, tipo="cliente") -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, password_hash, tipo),
        )
        self.connection.commit()
        return cursor.lastrowid
