"""Tratamento de erros centralizado — substitui os `except:` nus espalhados pelas rotas."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from shared.errors import ServiceError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ServiceError)
    def handle_service_error(error):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado")
        return jsonify({"error": "Erro interno"}), 500
