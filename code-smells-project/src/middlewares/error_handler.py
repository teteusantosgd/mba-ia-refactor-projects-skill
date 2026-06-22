"""Tratamento de erros centralizado.

Substitui os blocos `try/except Exception` espalhados pelos controllers. Erros
inesperados são logados internamente e respondidos com mensagem genérica, sem
vazar detalhes de implementação ao cliente.
"""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app) -> None:
    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno"}), 500
