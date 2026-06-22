"""Emissão de tokens JWT assinados para autenticação."""
from datetime import UTC, datetime, timedelta

import jwt


class TokenService:
    def __init__(self, secret_key, expiration_seconds):
        self.secret_key = secret_key
        self.expiration_seconds = expiration_seconds

    def issue_for(self, user):
        issued_at = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "iat": issued_at,
            "exp": issued_at + timedelta(seconds=self.expiration_seconds),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
