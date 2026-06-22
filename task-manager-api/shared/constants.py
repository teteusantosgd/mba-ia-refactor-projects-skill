"""Constantes de domínio — fonte única de verdade para regras e limites.

Substitui os magic numbers espalhados nas rotas e centraliza as listas de valores válidos.
"""

VALID_TASK_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_USER_ROLES = ["user", "admin", "manager"]

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PASSWORD_LENGTH = 4

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3

DEFAULT_CATEGORY_COLOR = "#000000"

RECENT_ACTIVITY_DAYS = 7
HIGH_PRIORITY_THRESHOLD = 2

EMAIL_REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
DUE_DATE_FORMAT = "%Y-%m-%d"
