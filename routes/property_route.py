from flask import Blueprint, request, jsonify
from services.supabase_client import supabase
from utils.auth_guard import require_auth
import uuid

property_bp = Blueprint("property", __name__)


@property_bp.route("/properties", methods=["POST"])
@require_auth
def create_property():
    try:
        data = request.json
        user_id = request.user["id"]

        # Insert into properties table
        property_data = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "description": data.get("description"),
            "location": data.get("location"),
            "rating": data.get("rating", 0),
            "review_count": data.get("review_count", 0),
            "main_image_url": data.get("main_image_url"),
            "owner_id": user_id,
        }

        prop_insert = supabase.table("properties").insert(property_data).execute()
        prop_id = property_data["id"]

        # Insert gallery images
        images = data.get("gallery_images", [])
        if images:
            image_data = [
                {"id": str(uuid.uuid4()), "property_id": prop_id, "image_url": url}
                for url in images
            ]
            supabase.table("property_images").insert(image_data).execute()

        # Insert facility relationships
        facility_ids = data.get("facility_ids", [])
        if facility_ids:
            facility_data = [
                {"id": str(uuid.uuid4()), "property_id": prop_id, "facility_id": fid}
                for fid in facility_ids
            ]
            supabase.table("property_facilities").insert(facility_data).execute()

        return jsonify({"message": "Property created", "property_id": prop_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@property_bp.route("/properties/<property_id>", methods=["GET"])
def get_property_by_id(property_id):
    try:
        # Get property info
        prop = (
            supabase.table("properties")
            .select("*")
            .eq("id", property_id)
            .single()
            .execute()
        )
        if not prop.data:
            return jsonify({"error": "Property not found"}), 404

        # Get gallery images
        images = (
            supabase.table("property_images")
            .select("image_url")
            .eq("property_id", property_id)
            .execute()
        )

        # Get facilities
        facilities_join = (
            supabase.table("property_facilities")
            .select("facility_id, facilities(name)")
            .eq("property_id", property_id)
            .execute()
        )

        print(facilities_join.data)

        # Get reviews (limit to 3)
        # Replace reviews table call
        reviews = (
            supabase.table("review_with_user_email")
            .select("*")
            .eq("property_id", property_id)
            .limit(3)
            .order("created_at", desc=True)
            .execute()
        )

        return (
            jsonify(
                {
                    "property": prop.data,
                    "images": [img["image_url"] for img in images.data],
                    "facilities": [
                        f["facilities"]["name"]
                        for f in facilities_join.data
                        if f.get("facilities")
                    ],
                    # "facilities": [f["facility_id"] for f in facilities_join.data],
                    # Access email directly
                    "reviews": [
                        {
                            "rating": r["rating"],
                            "text": r["review_text"],
                            "date": r["created_at"],
                            "user_email": r["user_email"],
                        }
                        for r in reviews.data
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@property_bp.route("/categories", methods=["GET"])
def get_all_categories():
    try:
        result = supabase.table("category").select("*").execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@property_bp.route("/properties", methods=["GET"])
def get_all_properties():
    try:
        category_id = request.args.get("category_id")
        search = request.args.get("search")

        query = supabase.table("properties").select("*")

        if category_id:
            query = query.eq("category_id", category_id)

        if search:
            query = query.or_(
                f"title.ilike.%{search}%,location.ilike.%{search}%"
            )

        result = query.order("created_at", desc=True).execute()
        properties = result.data

        all_properties = []

        for prop in properties:
            property_id = prop["id"]

            images_result = (
                supabase.table("property_images")
                .select("image_url")
                .eq("property_id", property_id)
                .limit(1)
                .execute()
            )

            reviews_result = (
                supabase.table("reviews")
                .select("rating")
                .eq("property_id", property_id)
                .execute()
            )

            category_result = (
                supabase.table("category")
                .select("name")
                .eq("id", prop.get("category_id"))
                .execute()
            )

            ratings = [r["rating"] for r in reviews_result.data]
            average_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

            all_properties.append(
                {
                    "id": prop["id"],
                    "title": prop["title"],
                    "location": prop.get("location"),
                    "category": category_result.data[0]["name"] if category_result.data else None,
                    "price_per_night": prop.get("price_per_night"),
                    "thumbnail": prop.get("main_image_url"),
                    "average_rating": average_rating,
                }
            )

        return jsonify(all_properties), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
