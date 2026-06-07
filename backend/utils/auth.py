from functools import wraps
from flask import request, jsonify, g
from models import User
from utils.security import decode_token


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "unauthorized"}), 401

        token = auth_header.split(" ")[1]
        data = decode_token(token)

        if not data:
            return jsonify({"error": "invalid token"}), 401

        user = User.query.get(data["user_id"])
        if not user:
            return jsonify({"error": "user not found"}), 401

        g.user = user

        return f(*args, **kwargs)

    return wrapper


def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(g, "user"):
                return jsonify({"error": "unauthorized"}), 401

            if g.user.role != role:
                return jsonify({"error": "forbidden"}), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator


def doctor_required(f):
    return require_role("doctor")(f)


def admin_required(f):
    return require_role("admin")(f)


def patient_required(f):
    return require_role("patient")(f)