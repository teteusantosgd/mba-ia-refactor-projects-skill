"""Gerenciamento da conexão com o banco e inicialização do schema.

A conexão é escopada por requisição via `flask.g` — sem singleton global
mutável. O schema e os dados de exemplo são criados uma única vez no startup
pela função `initialize_database`.
"""
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

from src.config import settings

_SEED_PRODUCTS = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

_SEED_USERS = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


def _create_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def get_connection() -> sqlite3.Connection:
    """Retorna a conexão da requisição atual, criando-a sob demanda."""
    if "db_connection" not in g:
        g.db_connection = _create_connection()
    return g.db_connection


def close_connection(_exception=None) -> None:
    """Fecha a conexão ao fim da requisição (registrado no teardown)."""
    connection = g.pop("db_connection", None)
    if connection is not None:
        connection.close()


def _create_schema(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            estoque INTEGER,
            categoria TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        )
        """
    )
    connection.commit()


def _seed_data(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] > 0:
        return

    cursor.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        _SEED_PRODUCTS,
    )
    hashed_users = [
        (name, email, generate_password_hash(password), user_type)
        for name, email, password, user_type in _SEED_USERS
    ]
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        hashed_users,
    )
    connection.commit()


def initialize_database() -> None:
    """Cria o schema e popula dados de exemplo uma única vez no startup."""
    connection = _create_connection()
    try:
        _create_schema(connection)
        _seed_data(connection)
    finally:
        connection.close()
