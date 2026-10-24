import requests
from flask import Blueprint, current_app, jsonify, request

from app.services.cafe_lookup import mark_existing_cafes

geoapify_bp = Blueprint("geoapify", __name__)


@geoapify_bp.route("/api/geoapify/autocomplete")
def geoapify_autocomplete():
    api_key = current_app.config.get("GEOAPIFY_API_KEY")

    if not api_key:
        current_app.logger.error("Geoapify API key is missing.")
        return jsonify({"error": "Geocoding service is not configured."}), 500

    allowed_params = ("text", "type", "limit", "format", "bias")
    params = {}

    for key in allowed_params:
        value = request.args.get(key)

        if value is not None:
            params[key] = value

    params["apiKey"] = api_key

    params_list = list(params.items())
    filters = request.args.getlist("filter")

    for value in filters:
        params_list.append(("filter", value))

    try:
        response = requests.get(
            "https://api.geoapify.com/v1/geocode/autocomplete",
            params=params_list,
            timeout=10,
        )
        data = response.json()

        if response.ok:
            data = mark_existing_cafes(data)
        return jsonify(data), response.status_code

    except requests.RequestException:
        current_app.logger.exception("Geoapify autocomplete request failed.")

        return jsonify({"error": "Geocoding service is temporarily unavailable."}), 502


@geoapify_bp.route("/api/geoapify/place-details")
def geoapify_place_details():
    api_key = current_app.config.get("GEOAPIFY_API_KEY")

    if not api_key:
        current_app.logger.error("Geoapify API key is missing.")
        return jsonify({"error": "Geocoding service is not configured."}), 500

    place_id = request.args.get("id", "").strip()

    if not place_id:
        return jsonify({"error": "Place ID is required."}), 400

    try:
        response = requests.get(
            "https://api.geoapify.com/v2/place-details",
            params={"id": place_id, "apiKey": api_key},
            timeout=10,
        )
        return jsonify(response.json()), response.status_code

    except requests.RequestException:
        current_app.logger.exception("Geoapify place-details request failed.")

        return jsonify({"error": "Geocoding service is temporarily unavailable."}), 502
