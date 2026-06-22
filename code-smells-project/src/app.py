"""Composition root: cria e configura a aplicação Flask.

Monta todas as peças (config, banco, rotas, middlewares) num único lugar.
"""
import logging

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.database import close_connection, initialize_database
from src.middlewares import register_error_handlers
from src.views import api


def create_app() -> Flask:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    initialize_database()

    app.register_blueprint(api)
    register_error_handlers(app)
    app.teardown_appcontext(close_connection)

    return app
