import os
from pathlib import Path
import uuid

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import select

from app.enums import OpeningDayStatus, CafeStatus, WeekDay
from app.extensions import db
from app.models import (Cafe,
                        CafeFeature,
                        OpeningHours,
                        CafePhoto,
                        Review,
                        )

from app.validators.suggestions import check_suggestion_data

suggestions_bp = Blueprint('suggestions', __name__)

PROJECT_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = PROJECT_DIR / "app" / "static" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def save_cafe_photo(photo, extension):
    unique_filename = f"{uuid.uuid4()}{extension}"
    photo_path = UPLOADS_DIR / unique_filename

    try:
        photo.save(photo_path)

    except OSError:
        try:
            photo_path.unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception(
                "Failed to remove incomplete photo: %s",
                photo_path,
            )
        raise

    relative_path = photo_path.relative_to(PROJECT_DIR / "app" / "static")

    return photo_path, relative_path.as_posix()


def add_opening_hours(new_cafe, cafe_opening_hours_data):
    for day, data in cafe_opening_hours_data.items():
        day_status = data["status"]
        intervals = (
            data["intervals"]
            if day_status == OpeningDayStatus.OPEN
            else [{}]
        )

        for interval in intervals:
            opening_time = interval.get("open")
            closing_time = interval.get("close")

            cafe_opening_hours = OpeningHours(
                day_of_week=WeekDay(day),
                status=day_status,
                open_time=opening_time,
                close_time=closing_time,
            )

            new_cafe.opening_hours.append(
                cafe_opening_hours
            )


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
     ) = check_suggestion_data(suggestion_json, photos)

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

    new_cafe = Cafe(**cafe_basic_info_data)
    new_cafe.status = CafeStatus.PENDING

    new_cafe_features = CafeFeature(**cafe_features_data)
    new_cafe.features = new_cafe_features

    add_opening_hours(new_cafe, cafe_opening_hours_data)

    new_cafe_review = Review(**cafe_review_data)
    new_cafe.reviews.append(new_cafe_review)

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

        for path in saved_photo_paths:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                current_app.logger.exception("Failed to remove uploaded photo: %s", path)

        raise

    return jsonify({
        "success": True
    }), 201
