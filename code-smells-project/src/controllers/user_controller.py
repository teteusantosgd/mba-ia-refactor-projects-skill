"""Controller de usuários e autenticação."""
from flask import jsonify, request

from src.container import build_user_service


def list_users():
    service = build_user_service()
    users = service.list_users()
    return jsonify({"dados": users, "sucesso": True}), 200


def get_user(id):
    service = build_user_service()
    user = service.get_user(id)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify({"dados": user, "sucesso": True}), 200


def create_user():
    service = build_user_service()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    user_id = service.create_user(nome, email, senha)
    return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201


def login():
    service = build_user_service()
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    user = service.authenticate(email, senha)
    if not user:
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    return jsonify({"dados": user, "sucesso": True, "mensagem": "Login OK"}), 200
