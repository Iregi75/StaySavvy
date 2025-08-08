from flask import Blueprint, jsonify
from services.supabase_client import supabase

hotel_bp = Blueprint("hotels", __name__)

@hotel_bp.route("/hotels", methods=["GET"])
def get_hotels():
    try:
        data = supabase.table("hotels").select("*").execute()
        return jsonify(data.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
