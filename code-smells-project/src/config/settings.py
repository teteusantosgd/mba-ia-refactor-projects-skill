"""Configuração da aplicação por ambiente.

Todos os segredos e parâmetros vêm de variáveis de ambiente. Nada de valor
sensível hardcoded no código-fonte (ver `.env.example`).
"""
import os
import secrets


def _read_secret_key() -> str:
    """Lê a SECRET_KEY do ambiente; gera uma efêmera em desenvolvimento.

    Em produção a variável deve estar sempre definida. Quando ausente, geramos
    uma chave aleatória por processo para nunca cair em um segredo hardcoded.
    """
    secret_key = os.environ.get("SECRET_KEY")
    if secret_key:
        return secret_key
    return secrets.token_hex(32)


class Settings:
    """Configuração imutável carregada do ambiente."""

    SECRET_KEY = _read_secret_key()
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    # Token exigido para operações administrativas destrutivas.
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
    APP_VERSION = "1.0.0"
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "producao")


settings = Settings()
