"""Definição das rotas (Blueprint). Apenas mapeia endpoints aos controllers.

As rotas preservam exatamente os caminhos, métodos e nomes do contrato original.
"""
from flask import Blueprint, jsonify

from src.controllers import (
    admin_controller,
    order_controller,
    product_controller,
    report_controller,
    user_controller,
)

api = Blueprint("api", __name__)

# Produtos
api.add_url_rule("/produtos", "listar_produtos", product_controller.list_products, methods=["GET"])
api.add_url_rule("/produtos/busca", "buscar_produtos", product_controller.search_products, methods=["GET"])
api.add_url_rule("/produtos/<int:id>", "buscar_produto", product_controller.get_product, methods=["GET"])
api.add_url_rule("/produtos", "criar_produto", product_controller.create_product, methods=["POST"])
api.add_url_rule("/produtos/<int:id>", "atualizar_produto", product_controller.update_product, methods=["PUT"])
api.add_url_rule("/produtos/<int:id>", "deletar_produto", product_controller.delete_product, methods=["DELETE"])

# Usuários
api.add_url_rule("/usuarios", "listar_usuarios", user_controller.list_users, methods=["GET"])
api.add_url_rule("/usuarios/<int:id>", "buscar_usuario", user_controller.get_user, methods=["GET"])
api.add_url_rule("/usuarios", "criar_usuario", user_controller.create_user, methods=["POST"])
api.add_url_rule("/login", "login", user_controller.login, methods=["POST"])

# Pedidos
api.add_url_rule("/pedidos", "criar_pedido", order_controller.create_order, methods=["POST"])
api.add_url_rule("/pedidos", "listar_todos_pedidos", order_controller.list_all_orders, methods=["GET"])
api.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", order_controller.list_user_orders, methods=["GET"])
api.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", order_controller.update_order_status, methods=["PUT"])

# Relatórios e health
api.add_url_rule("/relatorios/vendas", "relatorio_vendas", report_controller.sales_report, methods=["GET"])
api.add_url_rule("/health", "health_check", report_controller.health_check, methods=["GET"])

# Administração: reset protegido; executor SQL legado preservado apenas como rota descontinuada.
api.add_url_rule("/admin/reset-db", "reset_database", admin_controller.reset_database, methods=["POST"])
api.add_url_rule(
    "/admin/query",
    "retired_admin_query",
    admin_controller.retired_query_endpoint,
    methods=["POST"],
)


@api.route("/")
def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )
