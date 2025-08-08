from flask import Blueprint, request, jsonify
from services.supabase_client import supabase
from utils.auth_guard import require_auth

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    try:
        # First sign up the user
        sign_up_res = supabase.auth.sign_up({
            "email": data["email"],
            "password": data["password"],
            "options": {
                "data": {
                    "fullName": data.get("fullName"),
                    "phone": data.get("phone")
                }
                
            }
        })

        # Then immediately sign in to get the session
        sign_in_res = supabase.auth.sign_in_with_password({
            "email": data["email"],
            "password": data["password"]
        })

        return jsonify({
            "status": "success",
            "user": sign_in_res.user.dict() if sign_in_res.user else None,
            "session": sign_in_res.session.dict() if sign_in_res.session else None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400


@auth_bp.route("/submit-kyc", methods=["PUT"])
# @require_auth
def submit_kyc():
    data = request.json
    try:
        # access_token = request.headers.get("Authorization").split(" ")[1]

        # Update KYC data in user_metadata
        res = supabase.auth.update_user(
            {
                "data": {
                    "idType": data["idType"],
                    "idNumber": data["idNumber"],
                    "address": data["address"]
                }
            },
            # access_token=access_token
        )

        return jsonify({
            "status": "success",
            "user": res.user.dict() if res.user else None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400



@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data["email"],
            "password": data["password"]
        })

        return jsonify({
            "status": "success",
            "user": res.user.dict() if res.user else None,
            "session": res.session.dict() if res.session else None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400

@auth_bp.route("/update-user", methods=["PUT"])
@require_auth
def update_user():
    data = request.json
    try:
        update_data = {}

        # Optional fields to update
        if "email" in data:
            update_data["email"] = data["email"]
        if "password" in data:
            update_data["password"] = data["password"]
        if "user_metadata" in data:
            update_data["data"] = data["user_metadata"]

        # Use the access token from the auth header
        access_token = request.headers.get("Authorization").split(" ")[1]

        # res = supabase.auth.update_user(update_data, access_token=access_token)
        res = supabase.auth.update_user(update_data)


        return jsonify({
            "status": "success",
            "user": res.user.dict() if res.user else None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400


