"""Provedor de tempo.

Substitui o uso de `datetime.utcnow()` (deprecated no Python 3.12+). Retornamos o instante atual
em UTC, mas *naive*, para manter compatibilidade com os datetimes já persistidos no banco (SQLite
armazena valores sem timezone). Assim eliminamos a API deprecated sem quebrar comparações existentes.
"""
from datetime import UTC, datetime


def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)
