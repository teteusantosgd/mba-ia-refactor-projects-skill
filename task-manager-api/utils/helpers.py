"""Helpers utilitários genéricos e sem estado.

As constantes de domínio foram movidas para `shared/constants.py` e a validação de tasks para a
camada de service (`services/task_service.py`), eliminando duplicação.
"""
import re
from datetime import datetime

from shared.constants import DUE_DATE_FORMAT


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def sanitize_string(value):
    return value.strip() if value else value


def parse_date(date_string):
    for date_format in (DUE_DATE_FORMAT, "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, date_format)
        except (ValueError, TypeError):
            continue
    return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == "#"
