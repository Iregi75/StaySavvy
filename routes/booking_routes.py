from flask import Blueprint, request, jsonify
from services.supabase_client import supabase
from utils.auth_guard import require_auth

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/book", methods=["POST"])
@require_auth
def book_property():
    data = request.json
    print(data)
    try:
        booking_data = {
            "user_id": request.user.id,
            "property_id": data["property_id"],
            "check_in": data["check_in"],
            "check_out": data["check_out"],
            "guests": data["guests"],
            "payment_status": "paid",  # or "pending" depending on simulation
            "amount_paid": data["amount_paid"],
        }
        res = supabase.table("bookings").insert(booking_data).execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@booking_bp.route("/bookings/<user_id>", methods=["GET"])
@require_auth
def get_user_bookings(user_id):
    try:
        response = supabase.table("bookings").select(
            "id, payment_status, amount_paid, property_id, "
            "properties(title, property_images(image_url))"
        ).eq("user_id", user_id).execute()

        bookings = response.data

        formatted = []
        for booking in bookings:
            props = booking.get("properties", {})
            images = props.get("property_images", [])
            image_url = images[0]["image_url"] if images else None

            formatted.append({
                "id": booking["id"],
                "payment_status": booking["payment_status"],
                "price": booking["amount_paid"],
                "bnbName": props.get("title"),
                "imageUrl": image_url
            })

        return jsonify({"bookings": formatted})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



