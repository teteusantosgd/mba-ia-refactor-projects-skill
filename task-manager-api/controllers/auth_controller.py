from flask import jsonify, request

from container import auth_service
from serializers import serialize_user


def login():
    user = auth_service.login(request.get_json())
    return (
        jsonify(
            {
                "message": "Login realizado com sucesso",
                "user": serialize_user(user),
                "token": auth_service.issue_token(user),
            }
        ),
        200,
    )
