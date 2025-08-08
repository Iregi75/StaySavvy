from functools import wraps
from flask import request, jsonify
from services.supabase_client import supabase

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401

        token = auth_header.split(" ")[1]
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            return jsonify({"error": "Invalid or expired token"}), 401

        # ✅ Attach the actual user object
        request.user = user_response.user
        return func(*args, **kwargs)
    return wrapper

