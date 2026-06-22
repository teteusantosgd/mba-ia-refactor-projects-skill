"""Validações de domínio centralizadas.

Padrão: cada função retorna a mensagem de erro (em português) ou `None` quando
os dados são válidos. Uma única fonte de verdade reutilizada por create e update.
"""

VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 200


def validate_product(data: dict) -> str | None:
    if not data:
        return "Dados inválidos"
    if "nome" not in data:
        return "Nome é obrigatório"
    if "preco" not in data:
        return "Preço é obrigatório"
    if "estoque" not in data:
        return "Estoque é obrigatório"
    if data["preco"] < 0:
        return "Preço não pode ser negativo"
    if data["estoque"] < 0:
        return "Estoque não pode ser negativo"
    if len(data["nome"]) < MIN_NAME_LENGTH:
        return "Nome muito curto"
    if len(data["nome"]) > MAX_NAME_LENGTH:
        return "Nome muito longo"
    if data.get("categoria", "geral") not in VALID_CATEGORIES:
        return "Categoria inválida. Válidas: " + str(VALID_CATEGORIES)
    return None


def validate_order_status(status: str) -> str | None:
    if status not in VALID_ORDER_STATUSES:
        return "Status inválido"
    return None
