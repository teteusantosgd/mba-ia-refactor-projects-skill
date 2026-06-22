"""Controller de produtos: valida entrada, delega ao service, monta a resposta."""
from flask import jsonify, request

from src.container import build_product_service


def list_products():
    service = build_product_service()
    products = service.list_products()
    return jsonify({"dados": products, "sucesso": True}), 200


def get_product(id):
    service = build_product_service()
    product = service.get_product(id)
    if not product:
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    return jsonify({"dados": product, "sucesso": True}), 200


def create_product():
    service = build_product_service()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    result = service.create_product(data)
    if "erro" in result:
        return jsonify({"erro": result["erro"]}), 400
    return jsonify({"dados": {"id": result["id"]}, "sucesso": True, "mensagem": "Produto criado"}), 201


def update_product(id):
    service = build_product_service()
    data = request.get_json(silent=True)

    result = service.update_product(id, data or {})
    if result.get("not_found"):
        return jsonify({"erro": result["erro"]}), 404
    if "erro" in result:
        return jsonify({"erro": result["erro"]}), 400
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def delete_product(id):
    service = build_product_service()
    result = service.delete_product(id)
    if result.get("not_found"):
        return jsonify({"erro": result["erro"]}), 404
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def search_products():
    service = build_product_service()
    term = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    raw_min_price = request.args.get("preco_min", None)
    raw_max_price = request.args.get("preco_max", None)

    min_price = float(raw_min_price) if raw_min_price else None
    max_price = float(raw_max_price) if raw_max_price else None

    results = service.search_products(term, categoria, min_price, max_price)
    return jsonify({"dados": results, "total": len(results), "sucesso": True}), 200
