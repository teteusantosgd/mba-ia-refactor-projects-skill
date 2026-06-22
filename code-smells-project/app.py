"""Entry point da aplicação. Sobe o servidor a partir do composition root."""
import logging

from src.app import create_app
from src.config import settings

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    logger.info("Servidor iniciado em http://localhost:%s", settings.PORT)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
