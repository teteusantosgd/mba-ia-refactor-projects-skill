"""Controller de relatórios e health check."""
from flask import jsonify

from src.config import settings
from src.container import build_report_service
from src.database import get_connection


def sales_report():
    service = build_report_service()
    report = service.sales_report()
    return jsonify({"dados": report, "sucesso": True}), 200


def health_check():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    orders = cursor.fetchone()[0]

    return jsonify(
        {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": products,
                "usuarios": users,
                "pedidos": orders,
            },
            "versao": settings.APP_VERSION,
            "ambiente": settings.ENVIRONMENT,
        }
    ), 200
