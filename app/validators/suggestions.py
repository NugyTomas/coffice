import json
import os
import re

from PIL import Image, UnidentifiedImageError

from app.validators.common import check_optional_value
from app.validators.cafe import validate_cafe_basic_info_data
from app.validators.features import validate_cafe_features_data
from app.validators.opening_hours import validate_cafe_opening_hours_data

# =========================================
# CONSTANTS
# =========================================
INTEGER_PATTERN = re.compile(r"[0-9]+")

MAX_ALLOWED_PHOTOS = 6
ALLOWED_PHOTO_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
PHOTO_FORMATS_BY_EXTENSION = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}
MAX_ALLOWED_PHOTO_SIZE = 5 * 1024 * 1024

PHOTO_LIST_ERROR = "Cafe photos must be a list."
PHOTO_COUNT_ERROR = "Cafe photos must contain at most 6 photos."
PHOTO_TYPE_ERROR = "Only JPG, PNG and WebP photo types are allowed."
PHOTO_EXTENSION_MISMATCH_ERROR = "The image content does not match its file extension."
INVALID_PHOTO_ERROR = "The uploaded file is not a valid image."
PHOTO_SIZE_ERROR = "Maximum size of a photo is 5 MB."


# ============== DATA PARSING =============
def parse_suggestion_data(suggestion_json):
    errors = {}

    if not suggestion_json:
        errors["suggestion"] = "Missing suggestion data."
        return errors, None

    try:
        cafe_suggestion = json.loads(suggestion_json)
    except json.JSONDecodeError:
        errors["suggestion"] = "Invalid JSON data."
        return errors, None

    if not cafe_suggestion or not isinstance(cafe_suggestion, dict):
        errors["suggestion"] = "Invalid suggestion data."
        return errors, None

    return {}, cafe_suggestion


# =========== HELPER VALIDATORS ===========



def validate_cafe_review_data(cafe_review_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_review_data, dict):
        errors["cafe_review"] = "Cafe review data must be an object."
        return errors, None

    # =================== CAFE-RATING ======================
    cafe_rating = cafe_review_data.get("rating")

    if cafe_rating is None:
        errors["rating"] = "Cafe rating is required."

    elif isinstance(cafe_rating, bool):
        errors["rating"] = "Cafe rating must be a whole number."

    elif isinstance(cafe_rating, int):
        pass


    elif isinstance(cafe_rating, str):
        cafe_rating = cafe_rating.strip()

        if INTEGER_PATTERN.fullmatch(cafe_rating):
            cafe_rating = int(cafe_rating)

        else:
            errors["rating"] = "Cafe rating must be a whole number."

    else:
        errors["rating"] = "Cafe rating must be a whole number."

    if "rating" not in errors:
        if not (1 <= cafe_rating <= 5):
            errors["rating"] = "Invalid data! Please choose a rating between 1 and 5."
        else:
            cleaned["rating"] = cafe_rating

    # =================== CAFE-REVIEW ======================
    review_errors, cafe_review = check_optional_value("text", cafe_review_data, "Cafe review", 2048)
    errors |= review_errors

    if not review_errors and cafe_review is not None:
        cleaned["text"] = cafe_review

    return errors, cleaned


def validate_cafe_photos(cafe_photos):
    errors = {}

    if not isinstance(cafe_photos, list):
        errors["cafe_photos"] = PHOTO_LIST_ERROR
        return errors

    if len(cafe_photos) > MAX_ALLOWED_PHOTOS:
        errors["cafe_photos"] = PHOTO_COUNT_ERROR
        return errors

    for photo in cafe_photos:
        filename = photo.filename
        _, extension = os.path.splitext(filename)
        extension = extension.lower()

        error_key = f"cafe_photos_{filename}"

        if extension not in ALLOWED_PHOTO_TYPES:
            errors.setdefault(error_key, []).append(PHOTO_TYPE_ERROR)

        else:
            try:
                with Image.open(photo) as image:
                    actual_format = image.format
                    image.verify()

                expected_format = PHOTO_FORMATS_BY_EXTENSION[extension]

                if actual_format != expected_format:
                    errors.setdefault(error_key, []).append(PHOTO_EXTENSION_MISMATCH_ERROR)

            except (UnidentifiedImageError,
                    OSError,
                    Image.DecompressionBombError,
                    SyntaxError,
                    ValueError,):
                errors.setdefault(error_key, []).append(INVALID_PHOTO_ERROR)

            finally:
                photo.seek(0)

        photo.seek(0, os.SEEK_END)
        photo_size = photo.tell()
        photo.seek(0)

        if photo_size > MAX_ALLOWED_PHOTO_SIZE:
            errors.setdefault(error_key, []).append(PHOTO_SIZE_ERROR)

    return errors


def check_suggestion_data(suggestion_json, photos):
    errors, cafe_suggestion = parse_suggestion_data(suggestion_json)
    if errors:
        return errors, None, None, None, None, []

    # =================== CAFE_BASIC_INFO ======================
    cafe_basic_info_data = cafe_suggestion.get("cafe")
    errors, cafe_basic_info_data = validate_cafe_basic_info_data(cafe_basic_info_data)

    # =================== CAFE_FEATURES ======================
    cafe_features_data = cafe_suggestion.get("cafe_features")
    feature_errors, cafe_features_data = validate_cafe_features_data(cafe_features_data)
    errors |= feature_errors

    # =================== CAFE_OPENING_HOURS ======================
    cafe_opening_hours_data = cafe_suggestion.get("cafe_opening_hours")
    opening_hours_errors, cafe_opening_hours_data = validate_cafe_opening_hours_data(cafe_opening_hours_data)
    errors |= opening_hours_errors

    # =================== CAFE_REVIEW ======================
    cafe_review_data = cafe_suggestion.get("cafe_review")
    review_errors, cafe_review_data = validate_cafe_review_data(cafe_review_data)
    errors |= review_errors

    # =================== PHOTOS ======================
    cafe_photos = []
    if photos:
        photos_errors = validate_cafe_photos(photos)
        errors |= photos_errors
        cafe_photos = photos

    return errors, cafe_basic_info_data, cafe_features_data, cafe_opening_hours_data, cafe_review_data, cafe_photos
