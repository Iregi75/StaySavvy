import json
import os
from flask import Blueprint, request, jsonify
from services.supabase_client import supabase
from openai import OpenAI

ai_bp = Blueprint("ai", __name__)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@ai_bp.route("/ai-recommendations", methods=["POST"])
def ai_recommendations():
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Missing or empty query"}), 400

    system_prompt = """
    You are a filter assistant for a property booking app.
    Given a user's request, extract these fields and return JSON only:

    {
      "location": "city or town name (optional)",
      "category": "Apartment | Villa | Cottage | House | Any (optional)",
      "min_price": 0,
      "max_price": 5000,
      "must_have": ["wifi", "pool", ...] (list of desired facility names, optional)
    }

    Output ONLY valid JSON. Do not include any explanation or formatting.
    """

    try:
        # Step 1: Generate structured filter from user query
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )

        filters = json.loads(response.choices[0].message.content)

        # Step 2: Query base properties
        q = supabase.table("properties").select("*")

        # Filter: location
        if location := filters.get("location"):
            q = q.ilike("location", f"%{location}%")

        # Filter: category
        category_name = filters.get("category", "").strip().lower()
        if category_name and category_name != "any":
            category_res = supabase.table("category").select("id").ilike("name", f"%{category_name}%").limit(1).execute()
            if category_res.data:
                category_id = category_res.data[0]["id"]
                q = q.eq("category_id", category_id)

        # Filter: price range
        if filters.get("min_price") is not None:
            q = q.gte("price_per_night", filters["min_price"])
        if filters.get("max_price") is not None:
            q = q.lte("price_per_night", filters["max_price"])

        # Step 3: Execute initial query
        properties = q.execute().data or []

        # Step 4: Filter by must_have facilities
        must_have = [f.strip().lower() for f in filters.get("must_have", [])]
        if must_have:
            filtered = []
            for prop in properties:
                prop_id = prop["id"]
                facilities_res = (
                    supabase.table("property_facilities")
                    .select("facility_id, facilities(name)")
                    .eq("property_id", prop_id)
                    .execute()
                )

                facilities = [f["facilities"]["name"].strip().lower() for f in facilities_res.data or []]

                if all(item in facilities for item in must_have):
                    filtered.append(prop)
            properties = filtered

        # Step 5: Enrich properties for frontend (match /properties format)
        enriched_properties = []

        for prop in properties:
            property_id = prop["id"]

            # Thumbnail
            images_res = (
                supabase.table("property_images")
                .select("image_url")
                .eq("property_id", property_id)
                .limit(1)
                .execute()
            )
            thumbnail = images_res.data[0]["image_url"] if images_res.data else None

            # Rating
            reviews_res = (
                supabase.table("reviews")
                .select("rating")
                .eq("property_id", property_id)
                .execute()
            )
            ratings = [r["rating"] for r in reviews_res.data]
            average_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

            # Category
            category_res = (
                supabase.table("category")
                .select("name")
                .eq("id", prop.get("category_id"))
                .execute()
            )
            category_name = category_res.data[0]["name"] if category_res.data else None

            enriched_properties.append({
                "id": property_id,
                "title": prop["title"],
                "location": prop.get("location"),
                "category": category_name,
                "price_per_night": prop.get("price_per_night"),
                "thumbnail": thumbnail or prop.get("main_image_url"),
                "average_rating": average_rating,
            })

        return jsonify(enriched_properties), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
