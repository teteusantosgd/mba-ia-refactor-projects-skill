"""Erros de domínio usados pela camada de serviço.

Um service sinaliza falhas de negócio levantando `ServiceError(mensagem, status)`. O tratamento
HTTP fica centralizado no middleware de erros — controllers não precisam de try/except.
"""


class ServiceError(Exception):
    """Erro de negócio com mensagem amigável (em português) e status HTTP associado."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
