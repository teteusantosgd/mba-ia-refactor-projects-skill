"""Controller de operações administrativas (destrutivas, protegidas por token)."""
import logging

from flask import jsonify, request

from src.config import settings
from src.database import get_connection

logger = logging.getLogger(__name__)


def _is_authorized() -> bool:
    """Autoriza apenas quando ADMIN_TOKEN está configurado e confere com o header."""
    expected = settings.ADMIN_TOKEN
    provided = request.headers.get("X-Admin-Token")
    return bool(expected) and provided == expected


def reset_database():
    if not _is_authorized():
        return jsonify({"erro": "Não autorizado"}), 401

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    connection.commit()
    logger.warning("Banco de dados resetado via endpoint administrativo")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def retired_query_endpoint():
    """Preserva a rota legada sem permitir execução de SQL fornecido pelo cliente."""
    return (
        jsonify(
            {
                "erro": "Operação descontinuada por segurança",
                "sucesso": False,
            }
        ),
        410,
    )
