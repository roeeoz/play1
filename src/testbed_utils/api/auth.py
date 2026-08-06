"""Minimal token-based authentication and customer authorisation."""
from __future__ import annotations

from typing import NamedTuple

from flask import request


class AuthInfo(NamedTuple):
    actor_id: str
    allowed_customers: frozenset[str]


def decode_token(token: str, token_store: dict[str, AuthInfo]) -> AuthInfo | None:
    """Look up a bearer token and return the associated AuthInfo, or None if invalid."""
    return token_store.get(token)


def get_bearer_token() -> str | None:
    """Extract the bearer token from the Authorization header, or None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[len("Bearer "):].strip() or None


def require_auth(token_store: dict[str, AuthInfo]):
    """Decorator factory: authenticate the request and inject auth_info into kwargs."""
    from functools import wraps
    from flask import jsonify

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = get_bearer_token()
            if token is None:
                return jsonify({"error": "Unauthorized"}), 401
            auth_info = decode_token(token, token_store)
            if auth_info is None:
                return jsonify({"error": "Unauthorized"}), 401
            kwargs["auth_info"] = auth_info
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def authorize_customer(auth_info: AuthInfo, customer_id: str) -> bool:
    """Return True if the actor is authorised to access the given customer."""
    return customer_id in auth_info.allowed_customers
