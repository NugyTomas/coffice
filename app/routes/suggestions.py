from flask import Blueprint, jsonify, request

from app.constants import ANONYMOUS_USER_ID
from app.services.suggestions import DuplicateCafeError, create_cafe_suggestion
from app.validators.suggestions import validate_suggestion_data

# =================== CONSTANT ======================
DUPLICATE_CAFE_ERROR = "The cafe is already submitted or waiting for approval."

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

    try:
        create_cafe_suggestion(
            basic_info=cafe_basic_info_data,
            features=cafe_features_data,
            opening_hours=cafe_opening_hours_data,
            review=cafe_review_data,
            photos=cafe_photos,
            submitted_by_id=ANONYMOUS_USER_ID,
        )
    except DuplicateCafeError:
        return jsonify({
            "success": False,
            "errors": {
                "cafe": DUPLICATE_CAFE_ERROR
            }
        }), 409

    return jsonify({
        "success": True
    }), 201
