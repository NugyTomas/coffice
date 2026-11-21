import os

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.constants import ANONYMOUS_USER_ID
from app.extensions import db
from app.models import (Cafe,
                        CafePhoto,
                        )
from app.services.photos import save_cafe_photo, delete_photo_files
from app.services.suggestions import build_cafe_suggestion
from app.validators.suggestions import validate_suggestion_data

suggestions_bp = Blueprint('suggestions', __name__)


@suggestions_bp.route("/api/cafe-suggestions", methods=['POST'])
def create_cafe_suggestion():
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
    external_id = cafe_basic_info_data.get("external_place_id")

    if external_id:
        exists = (db.session.scalar(
            select(Cafe.id).where(Cafe.external_place_id == external_id)))

        if exists:
            return jsonify({
                "success": False,
                "errors": {"cafe": "This café is already on Coffice or waiting for approval."}
            }), 409

    new_cafe = build_cafe_suggestion(
        cafe_basic_info_data,
        cafe_features_data,
        cafe_opening_hours_data,
        cafe_review_data,
        ANONYMOUS_USER_ID,
    )

    saved_photo_paths = []

    try:
        for photo in cafe_photos:
            _, extension = os.path.splitext(photo.filename)
            photo_path, image_url = save_cafe_photo(photo, extension)
            saved_photo_paths.append(photo_path)

            new_cafe_photo = CafePhoto(
                image_url=image_url
            )
            new_cafe.photos.append(new_cafe_photo)

        db.session.add(new_cafe)
        db.session.commit()

    except Exception:
        db.session.rollback()
        delete_photo_files(saved_photo_paths)

        raise

    return jsonify({
        "success": True
    }), 201
