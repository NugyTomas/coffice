import os
import requests
import uuid
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from sqlalchemy import select

from app.enums import (OpeningDayStatus)
from app.extensions import db
from app.models import (Cafe,
                        CafeSuggestion,
                        CafeSuggestionOpeningHours,
                        CafeSuggestionPhoto,
                        CafeSuggestionFeature,
                        CafeSuggestionReview)

from app.validators.suggestions import check_suggestion_data


load_dotenv()
# =========================================
# CONSTANTS
# =========================================
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# =================== PATHS SETUP ======================
PROJECT_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = PROJECT_DIR / "app" / "static" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# =========================================
# FLASK
# =========================================
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coffice.db"
db.init_app(app)

with app.app_context():
    db.create_all()

# ============ PHOTO HANDLING =============
def save_cafe_photo(photo, extension):
    unique_filename = f"{uuid.uuid4()}{extension}"
    photo_path = UPLOADS_DIR / unique_filename

    try:
        photo.save(photo_path)

    except OSError:
        try:
            photo_path.unlink(missing_ok=True)
        except OSError:
            app.logger.exception(
                "Failed to remove incomplete photo: %s",
                photo_path,
            )
        raise

    relative_path = photo_path.relative_to(PROJECT_DIR / "app" / "static")

    return photo_path, relative_path.as_posix()

# ======== PROCESSING AND HELPERS ===========

def mark_existing_cafes(data):
    results = data.get("results", [])
    place_ids = []
    for result in results:
        if result.get("category") == "catering.cafe" and result.get("place_id"):
            place_ids.append(result["place_id"])

    if not place_ids:
        return data

    approved = set(db.session.scalars(select(Cafe.external_place_id).where(Cafe.external_place_id.in_(place_ids))))
    pending = set(db.session.scalars(select(CafeSuggestion.external_place_id).where(CafeSuggestion.external_place_id.in_(place_ids))))

    for result in results:
        if result.get("place_id") in approved:
            result["coffice_status"] = "approved"
        elif result.get("place_id") in pending:
            result["coffice_status"] = "pending"

    return data

def add_suggestion_opening_hours(cafe_suggestion, cafe_opening_hours_data):
    for day, data in cafe_opening_hours_data.items():
        day_status = data['status']
        intervals = data["intervals"] if day_status == OpeningDayStatus.OPEN else [{}]

        for interval in intervals:
            opening_time = interval.get('open')
            closing_time = interval.get('close')
            new_cafe_opening_hours_suggestion = CafeSuggestionOpeningHours(
                day_of_week=day,
                status=day_status,
                open_time=opening_time,
                close_time=closing_time
            )
            cafe_suggestion.suggestion_opening_hours.append(new_cafe_opening_hours_suggestion)

# =========================================
# ROUTES
# =========================================
@app.route("/api/geoapify/autocomplete")
def geoapify_autocomplete():
    if not GEOAPIFY_API_KEY:
        app.logger.error("Geoapify API key is missing.")
        return jsonify({"error": "Geocoding service is not configured."}), 500

    allowed_params = ("text", "type", "limit", "format", "bias")
    params = {
        key: request.args.get(key)
        for key in allowed_params
        if request.args.get(key) is not None
    }

    params["apiKey"] = GEOAPIFY_API_KEY

    # Preserve multiple filter parameters, if provided.
    params_list = list(params.items())
    params_list.extend(("filter", value) for value in request.args.getlist("filter"))

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
        app.logger.exception("Geoapify autocomplete request failed.")
        return jsonify({"error": "Geocoding service is temporarily unavailable."}), 502


@app.route("/api/geoapify/place-details")
def geoapify_place_details():
    if not GEOAPIFY_API_KEY:
        app.logger.error("Geoapify API key is missing.")
        return jsonify({"error": "Geocoding service is not configured."}), 500

    place_id = request.args.get("id", "").strip()
    if not place_id:
        return jsonify({"error": "Place ID is required."}), 400

    try:
        response = requests.get(
            "https://api.geoapify.com/v2/place-details",
            params={"id": place_id, "apiKey": GEOAPIFY_API_KEY},
            timeout=10,
        )
        return jsonify(response.json()), response.status_code

    except requests.RequestException:
        app.logger.exception("Geoapify place-details request failed.")
        return jsonify({"error": "Geocoding service is temporarily unavailable."}), 502

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/suggest-cafe')
def suggest_cafe():
    return render_template("suggest-cafe.html")


@app.route("/api/cafe-suggestions", methods=['POST'])
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
        exists = (db.session.scalar(select(Cafe.id).where(Cafe.external_place_id == external_id))
                or db.session.scalar(select(CafeSuggestion.id).where(CafeSuggestion.external_place_id == external_id)))

        if exists:
            return jsonify({
                "success": False,
                "errors": {"cafe": "This café is already on Coffice or waiting for approval."}
            }), 409

    new_cafe_suggestion = CafeSuggestion(**cafe_basic_info_data)
    new_cafe_features_suggestion = CafeSuggestionFeature(**cafe_features_data)
    new_cafe_suggestion.suggestion_features = new_cafe_features_suggestion

    add_suggestion_opening_hours(new_cafe_suggestion, cafe_opening_hours_data)

    new_cafe_review_suggestion = CafeSuggestionReview(**cafe_review_data)
    new_cafe_suggestion.suggestion_reviews = new_cafe_review_suggestion

    saved_photo_paths = []

    try:
        for photo in cafe_photos:
            _, extension = os.path.splitext(photo.filename)
            photo_path, image_url = save_cafe_photo(photo, extension)
            saved_photo_paths.append(photo_path)

            new_cafe_photo = CafeSuggestionPhoto(
                image_url=image_url
            )
            new_cafe_suggestion.suggestion_photos.append(new_cafe_photo)

        db.session.add(new_cafe_suggestion)
        db.session.commit()

    except Exception:
        db.session.rollback()

        for path in saved_photo_paths:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                app.logger.exception("Failed to remove uploaded photo: %s", path)

        raise

    return jsonify({
        "success": True
    }), 201


# =========================================
# APPLICATION ENTRY POINT
# =========================================

if __name__ == "__main__":
    app.run(debug=True)
