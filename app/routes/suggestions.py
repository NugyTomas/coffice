from flask import Blueprint, jsonify, request

from app.constants import ANONYMOUS_USER_ID
from app.services.suggestions import create_cafe_suggestion
from app.validators.suggestions import validate_suggestion_data

suggestions_bp = Blueprint('suggestions', __name__)


@suggestions_bp.route("/api/cafe-suggestions", methods=['POST'])
def submit_cafe_suggestion():
    suggestion_json = request.form.get("suggestion")
    photos = request.files.getlist("photos")

    (errors,
     cafe_basic_info_data,
     cafe_features_data,
     cafe_opening_hours_data,
     cafe_review_data,
     cafe_photos
     ) = validate_suggestion_data(suggestion_json, photos)

    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    create_cafe_suggestion(
        cafe_basic_info_data,
        cafe_features_data,
        cafe_opening_hours_data,
        cafe_review_data,
        cafe_photos,
        ANONYMOUS_USER_ID,
    )

    return jsonify({
        "success": True
    }), 201
