"""Controller de pedidos."""
from flask import jsonify, request

from src.container import build_order_service


def create_order():
    service = build_order_service()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])
    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    result = service.create_order(usuario_id, itens)
    if "erro" in result:
        return jsonify({"erro": result["erro"], "sucesso": False}), 400

    return jsonify({"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def list_user_orders(usuario_id):
    service = build_order_service()
    orders = service.list_user_orders(usuario_id)
    return jsonify({"dados": orders, "sucesso": True}), 200


def list_all_orders():
    service = build_order_service()
    orders = service.list_all_orders()
    return jsonify({"dados": orders, "sucesso": True}), 200


def update_order_status(pedido_id):
    service = build_order_service()
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "")

    result = service.update_status(pedido_id, new_status)
    if "erro" in result:
        return jsonify({"erro": result["erro"]}), 400
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
