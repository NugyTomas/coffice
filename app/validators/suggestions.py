from datetime import datetime
import json
import os
import re

from email_validator import validate_email, EmailNotValidError
from flask import current_app
from PIL import Image, UnidentifiedImageError

from app.enums import (CafePrice,
                       CoffeeQuality,
                       WifiQuality,
                       PowerOutlets,
                       NoiseLevel,
                       Seating,
                       AirConditioning,
                       TypicalOccupancy,
                       FoodOptions,
                       VegetarianOptions,
                       CardPayment,
                       WeekDay,
                       OpeningDayStatus,
                       )

# =========================================
# CONSTANTS
# =========================================
POSTAL_CODE_PATTERN = re.compile(r"[0-9]{3} [0-9]{2}")
PHONE_PATTERN = re.compile(r"[0-9]{3} [0-9]{3} [0-9]{3}")
WEBSITE_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}(/.*)?")
INSTAGRAM_PATTERN = re.compile(r"[a-z0-9_]+(\.[a-z0-9_]+)*")
TIME_TEXT_PATTERN = re.compile(r"\d{2}:\d{2}")
INTEGER_PATTERN = re.compile(r"[0-9]+")
TIME_FORMAT = "%H:%M"
MAX_ALLOWED_PHOTOS = 6
ALLOWED_PHOTO_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
PHOTO_FORMATS_BY_EXTENSION = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}
MAX_ALLOWED_PHOTO_SIZE = 5 * 1024 * 1024


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
def validate_text_field(field_name, data, min_length, max_length, require_letter=False):
    errors = {}
    value = None

    text = data.get(field_name)

    if text is None:
        errors[field_name] = f"{field_name.capitalize()} is required."

    elif not isinstance(text, str):
        errors[field_name] = f"{field_name.capitalize()} must be a text."

    else:
        text = text.strip()

        if not text:
            errors[field_name] = f"{field_name.capitalize()} cannot be empty."

        elif len(text) < min_length:
            errors[field_name] = f"{field_name.capitalize()} must contain at least {min_length} characters."

        elif len(text) > max_length:
            errors[field_name] = f"{field_name.capitalize()} must contain at most {max_length} characters."

        elif require_letter and not re.search(r"[^\W\d_]", text):
            errors[field_name] = f"{field_name.capitalize()} must contain at least one letter."

        else:
            value = text

    return errors, value


def validate_choice(field_name, data, field_label, enum_class):
    errors = {}
    value = None

    text = data.get(field_name)

    if text is None:
        errors[field_name] = f"{field_label.capitalize()} is required."
    elif not isinstance(text, str):
        errors[field_name] = f"{field_label.capitalize()} must be a text."
    else:
        text = text.strip()

        if not text:
            errors[field_name] = f"{field_label.capitalize()} cannot be empty."
        else:
            try:
                choice = enum_class(text)
            except ValueError:
                errors[field_name] = f"Invalid data! Please choose one of the options."
            else:
                value = choice

    return errors, value


def validate_coordinate(coordinate, data, min_limit, max_limit):
    errors = {}
    value = data.get(coordinate)
    validated_value = None

    if value is None:
        errors[coordinate] = f"{coordinate.capitalize()} is required."
    elif isinstance(value, bool) or not isinstance(value, (int, float)):
        errors[coordinate] = f"{coordinate.capitalize()} must be a number."
    elif not (min_limit <= value <= max_limit):
        errors[coordinate] = f"{coordinate.capitalize()} is out of range."
    else:
        validated_value = float(value)

    return errors, validated_value


# ============== VALIDATORS ===============
def validate_cafe_basic_info_data(cafe_basic_info_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_basic_info_data, dict):
        errors["cafe"] = "Cafe data must be an object."
        return errors, None

    # =================== EXTERNAL_PLACE_ID ======================
    cafe_external_id = cafe_basic_info_data.get("external_place_id")

    if cafe_external_id is not None:
        if not isinstance(cafe_external_id, str):
            errors["external_place_id"] = "External ID of a cafe must be a text."
        else:
            cafe_external_id = cafe_external_id.strip()

            if cafe_external_id:
                if len(cafe_external_id) > 255:
                    errors["external_place_id"] = "External ID must contain at most 255 characters."
                else:
                    cleaned["external_place_id"] = cafe_external_id

    # =================== NAME ======================
    text_field_errors, value = validate_text_field("name", cafe_basic_info_data, 2, 50)
    errors |= text_field_errors

    if not text_field_errors:
        cleaned["name"] = value

    # =================== ADDRESS ======================
    text_field_errors, value = validate_text_field("address", cafe_basic_info_data, 3, 100, require_letter=True)
    errors |= text_field_errors

    if not text_field_errors:
        cleaned["address"] = value

    # =================== CITY ======================
    text_field_errors, value = validate_text_field("city", cafe_basic_info_data, 2, 50, require_letter=True)
    errors |= text_field_errors

    if not text_field_errors:
        cleaned["city"] = value

    # =================== POSTAL CODE ======================
    cafe_postal_code = cafe_basic_info_data.get("postal_code")

    if not cafe_postal_code:
        errors["postal_code"] = "Postal code is required."

    elif not isinstance(cafe_postal_code, str):
        errors["postal_code"] = "Postal code must be a text."

    else:
        cafe_postal_code = cafe_postal_code.strip()

        if not cafe_postal_code:
            errors["postal_code"] = "Postal code cannot be empty."

        elif not POSTAL_CODE_PATTERN.fullmatch(cafe_postal_code):
            errors["postal_code"] = "Postal code must be in format 'XXX XX'."

        else:
            cleaned["postal_code"] = cafe_postal_code

    # =================== PHONE ======================
    cafe_phone_number = cafe_basic_info_data.get("phone")

    if cafe_phone_number is not None:

        if not isinstance(cafe_phone_number, str):
            errors["phone"] = "Phone number must be a text."

        else:
            cafe_phone_number = cafe_phone_number.strip()

            if cafe_phone_number:
                if not PHONE_PATTERN.fullmatch(cafe_phone_number):
                    errors["phone"] = "Phone number must be in format 'XXX XXX XXX'. We will add +420 for you."

                else:
                    cleaned["phone"] = "+420 " + cafe_phone_number

    # =================== EMAIL ======================
    cafe_email = cafe_basic_info_data.get("email")

    if cafe_email is not None:
        if not isinstance(cafe_email, str):
            errors["email"] = "Email must be a text."

        else:
            cafe_email = cafe_email.strip()

            if cafe_email:
                if len(cafe_email) > 250:
                    errors["email"] = "Email must contain at most 250 characters."

                else:
                    try:
                        email_validator = validate_email(cafe_email, check_deliverability=current_app.config[
                            "CHECK_EMAIL_DELIVERABILITY"])
                        cleaned["email"] = email_validator.normalized

                    except EmailNotValidError:
                        errors["email"] = "Email is not valid."

    # =================== WEBSITE ======================
    cafe_website = cafe_basic_info_data.get("website")

    if cafe_website is not None:
        if not isinstance(cafe_website, str):
            errors["website"] = "Website must be a text."

        else:
            cafe_website = cafe_website.strip()

            if cafe_website:
                lowered_cafe_website = cafe_website.lower()

                if lowered_cafe_website.startswith("http://"):
                    cafe_website = "https://" + cafe_website[7:]

                elif lowered_cafe_website.startswith("https://"):
                    cafe_website = "https://" + cafe_website[8:]

                else:
                    cafe_website = "https://" + cafe_website

                if len(cafe_website) > 2048:
                    errors["website"] = "Website must contain at most 2048 characters."

                elif not WEBSITE_PATTERN.fullmatch(cafe_website):
                    errors["website"] = "Website is not valid."

                else:
                    cleaned["website"] = cafe_website

    # =================== INSTAGRAM ======================
    cafe_instagram = cafe_basic_info_data.get("instagram")

    if cafe_instagram is not None:
        if not isinstance(cafe_instagram, str):
            errors["instagram"] = "Instagram username must be a text."

        else:
            cafe_instagram = cafe_instagram.strip().lower().removeprefix("@")

            if cafe_instagram:

                if len(cafe_instagram) > 30:
                    errors["instagram"] = "Instagram username must contain at most 30 characters."

                elif not INSTAGRAM_PATTERN.fullmatch(cafe_instagram):
                    errors[
                        "instagram"] = "Instagram username can contain only letters, numbers, dots and underscores. A dot cannot be first, last or doubled."

                else:
                    cleaned["instagram"] = "@" + cafe_instagram

    # =================== PRICE-LEVEL, COFFEE_QUALITY ======================
    option_fields = [
        ("price_level", "price level", CafePrice),
        ("coffee_quality", "coffee quality", CoffeeQuality),
    ]

    for (name, label, enum) in option_fields:
        choice_errors, value = validate_choice(name, cafe_basic_info_data, label, enum)
        errors |= choice_errors

        if not choice_errors:
            cleaned[name] = value

    # =================== LATITUDE ======================
    coordinate_errors, value = validate_coordinate("latitude", cafe_basic_info_data, -90, 90)
    errors |= coordinate_errors

    if not coordinate_errors:
        cleaned["latitude"] = value

    # =================== LONGITUDE ======================
    coordinate_errors, value = validate_coordinate("longitude", cafe_basic_info_data, -180, 180)
    errors |= coordinate_errors

    if not coordinate_errors:
        cleaned["longitude"] = value

    return errors, cleaned


def validate_cafe_features_data(cafe_features_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_features_data, dict):
        errors["features"] = "Cafe features data must be an object."
        return errors, None

    feature_fields = [
        ("wifi_quality", "wifi quality", WifiQuality),
        ("power_outlets", "power outlets", PowerOutlets),
        ("noise_level", "noise level", NoiseLevel),
        ("seating_type", "seating type", Seating),
        ("air_conditioning", "air conditioning", AirConditioning),
        ("typical_occupancy", "typical occupancy", TypicalOccupancy),
        ("food_options", "food options", FoodOptions),
        ("vegetarian_options", "vegetarian options", VegetarianOptions),
        ("card_payment", "card payment", CardPayment),
    ]

    for (name, label, enum) in feature_fields:
        choice_errors, value = validate_choice(name, cafe_features_data, label, enum)
        errors |= choice_errors

        if not choice_errors:
            cleaned[name] = value

    return errors, cleaned


def validate_cafe_opening_hours_data(cafe_opening_hours_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_opening_hours_data, dict):
        errors["opening_hours"] = "Cafe opening hours data must be an object."
        return errors, None

    for day in WeekDay:
        day_name = day.value

        if day_name not in cafe_opening_hours_data:
            errors[f"opening_hours_{day_name}"] = f"Opening hours status for {day_name.capitalize()} is required."
            continue

        day_data = cafe_opening_hours_data[day_name]

        if not isinstance(day_data, dict):
            errors[f"opening_hours_{day_name}"] = f"Opening hours data for {day_name.capitalize()} must be an object."
            continue

        cafe_day_status = day_data.get("status")
        if cafe_day_status is None:
            errors[
                f"opening_hours_{day_name}_status"] = f"Opening hours status for {day_name.capitalize()} is required."
            continue

        if not isinstance(cafe_day_status, str):
            errors[
                f"opening_hours_{day_name}_status"] = f"Opening hours status for {day_name.capitalize()} must be a string."
            continue

        try:
            cafe_day_status = OpeningDayStatus(cafe_day_status)
        except ValueError:
            errors[f"opening_hours_{day_name}_status"] = f"Invalid opening hours status for {day_name.capitalize()}."
            continue

        cleaned[day_name] = {}
        cleaned[day_name]["status"] = cafe_day_status

        cafe_day_intervals = day_data.get("intervals")
        if cafe_day_intervals is None:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} are required (use an empty list [] if closed)."
            continue

        if not isinstance(cafe_day_intervals, list):
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be a list."
            continue

        if cafe_day_status is not OpeningDayStatus.OPEN and cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be empty when the café is not open."
            continue

        cleaned[day_name]["intervals"] = []

        if cafe_day_status is not OpeningDayStatus.OPEN:
            continue

        if not cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} are required when the café is open."
            continue

        if len(cafe_day_intervals) > 2:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} can contain at most two intervals."
            continue

        previous_close_time = None

        for interval in cafe_day_intervals:
            if not isinstance(interval, dict):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours interval for {day_name.capitalize()} must be an object."
                continue

            if set(interval.keys()) != {"open", "close"}:
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours interval for {day_name.capitalize()} must contain only 'open' and 'close'."
                continue

            open_time_text = interval["open"]
            close_time_text = interval["close"]

            if not isinstance(open_time_text, str) or not isinstance(close_time_text, str):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening and closing times for {day_name.capitalize()} must be strings."
                continue

            if not TIME_TEXT_PATTERN.fullmatch(open_time_text) or not TIME_TEXT_PATTERN.fullmatch(close_time_text):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue

            try:
                open_time = datetime.strptime(open_time_text, TIME_FORMAT).time()
                close_time = datetime.strptime(close_time_text, TIME_FORMAT).time()
            except ValueError:
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue
            else:
                if previous_close_time is not None and open_time < previous_close_time:
                    errors[
                        f"opening_hours_{day_name}_intervals"] = f"Opening intervals for {day_name.capitalize()} must not overlap."
                    continue

                cleaned[day_name]["intervals"].append({
                    "open": open_time,
                    "close": close_time
                })

                previous_close_time = close_time

    return errors, cleaned


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
    cafe_review = cafe_review_data.get("text")

    if cafe_review is not None:
        if not isinstance(cafe_review, str):
            errors["text"] = "Cafe review must be a text."
        else:
            cafe_review = cafe_review.strip()

            if cafe_review:
                if len(cafe_review) > 2048:
                    errors["text"] = "Cafe review must contain at most 2048 characters."
                else:
                    cleaned["text"] = cafe_review

    return errors, cleaned


def validate_cafe_photos(cafe_photos):
    errors = {}

    if not isinstance(cafe_photos, list):
        errors["cafe_photos"] = "Cafe photos must be a list."
        return errors

    if len(cafe_photos) > MAX_ALLOWED_PHOTOS:
        errors["cafe_photos"] = "Cafe photos must contain at most 6 photos."
        return errors

    for photo in cafe_photos:
        filename = photo.filename
        _, extension = os.path.splitext(filename)
        extension = extension.lower()

        error_key = f"cafe_photos_{filename}"

        if extension not in ALLOWED_PHOTO_TYPES:
            errors.setdefault(error_key, []).append("Only JPG, PNG and WebP photo types are allowed.")

        else:
            try:
                with Image.open(photo) as image:
                    actual_format = image.format
                    image.verify()

                expected_format = PHOTO_FORMATS_BY_EXTENSION[extension]

                if actual_format != expected_format:
                    errors.setdefault(error_key, []).append("The image content does not match its file extension.")

            except (UnidentifiedImageError,
                    OSError,
                    Image.DecompressionBombError,
                    SyntaxError,
                    ValueError,):
                errors.setdefault(error_key, []).append("The uploaded file is not a valid image.")

            finally:
                photo.seek(0)

        photo.seek(0, os.SEEK_END)
        photo_size = photo.tell()
        photo.seek(0)

        if photo_size > MAX_ALLOWED_PHOTO_SIZE:
            errors.setdefault(f"cafe_photos_{filename}", []).append("Maximum size of a photo is 5 MB.")

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
