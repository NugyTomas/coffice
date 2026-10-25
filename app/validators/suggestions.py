from datetime import datetime
import json
import os
import re


from email_validator import validate_email, EmailNotValidError
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
                       Rating)


# =========================================
# CONSTANTS
# =========================================
POSTAL_CODE_PATTERN = re.compile(r"[0-9]{3} [0-9]{2}")
PHONE_PATTERN = re.compile(r"[0-9]{3} [0-9]{3} [0-9]{3}")
WEBSITE_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}(/.*)?")
INSTAGRAM_PATTERN = re.compile(r"[a-z0-9_]+(\.[a-z0-9_]+)*")
TIME_TEXT_PATTERN = re.compile(r"\d{2}:\d{2}")
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
            data[field_name] = text

    return errors

def validate_choice(field_name, data, field_label, enum_class):
    errors = {}
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
                data[field_name] = choice

    return errors

def validate_coordinate(coordinate, data, min_limit, max_limit):
    errors = {}
    text = data.get(coordinate)

    if text is not None:
        try:
            text = float(text)
            if min_limit <= text <= max_limit:
                data[coordinate] = text
            else:
                errors[coordinate] = f"{coordinate.capitalize()} is out of range."
                data[coordinate] = None
        except (TypeError, ValueError):
            errors[coordinate] = "Invalid data type"
            data[coordinate] = None
    else:
        data[coordinate] = None

    return errors


# ============== VALIDATORS ===============
def validate_cafe_basic_info_data(cafe_basic_info_data):
    errors = {}

    if not isinstance(cafe_basic_info_data, dict):
        errors["cafe"] = "Cafe data must be an object."
        return errors, None


    # =================== CAFE_EXTERNAL_ID ======================
    cafe_external_id = cafe_basic_info_data.get("external_place_id")

    if cafe_external_id is not None:
        if not isinstance(cafe_external_id, str):
            errors["cafe_external_id"] = "External ID of a cafe must be a text."
        else:
            cafe_external_id = cafe_external_id.strip()

            if cafe_external_id:
                if len(cafe_external_id) > 255:
                    errors["cafe_external_id"] = "External ID must contain at most 255 characters."
                else:
                    cafe_basic_info_data["external_place_id"] = cafe_external_id

            else:
                cafe_basic_info_data["external_place_id"] = None

    # =================== NAME ======================
    errors |= validate_text_field("name", cafe_basic_info_data, 2, 50)

    # =================== ADDRESS ======================
    errors |= validate_text_field("address", cafe_basic_info_data, 3, 100, require_letter=True)

    # =================== CITY ======================
    errors |= validate_text_field("city", cafe_basic_info_data, 2, 50, require_letter=True)

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
            cafe_basic_info_data["postal_code"] = cafe_postal_code

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
                    cafe_basic_info_data["phone"] = "+420 " + cafe_phone_number

            else:
                cafe_basic_info_data["phone"] = None

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
                        email_validator = validate_email(cafe_email, check_deliverability=True)
                        cafe_basic_info_data["email"] = email_validator.normalized

                    except EmailNotValidError:
                        errors["email"] = "Email is not valid."

            else:
                cafe_basic_info_data["email"] = None

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
                    cafe_basic_info_data["website"] = cafe_website

            else:
                cafe_basic_info_data["website"] = None

    # =================== INSTAGRAM ======================
    cafe_instagram = cafe_basic_info_data.get("instagram")

    if cafe_instagram is not None:
        if not isinstance(cafe_instagram, str):
            errors["instagram"] = "Instagram username must be a text."

        else:
            cafe_instagram = cafe_instagram.strip().lower().removeprefix("@")

            if not cafe_instagram:
                cafe_basic_info_data["instagram"] = None

            elif len(cafe_instagram) > 30:
                errors["instagram"] = "Instagram username must contain at most 30 characters."

            elif not INSTAGRAM_PATTERN.fullmatch(cafe_instagram):
                errors[
                    "instagram"] = "Instagram username can contain only letters, numbers, dots and underscores. A dot cannot be first, last or doubled."

            else:
                cafe_basic_info_data["instagram"] = "@" + cafe_instagram

    # =================== PRICE-LEVEL ======================
    errors |= validate_choice("price_level", cafe_basic_info_data, "price level", CafePrice)

    # =================== COFFEE-QUALITY ======================
    errors |= validate_choice("coffee_quality", cafe_basic_info_data, "coffee quality", CoffeeQuality)

    # =================== LATITUDE ======================
    errors |= validate_coordinate("latitude", cafe_basic_info_data, -90, 90)

    # =================== LONGITUDE ======================
    errors |= validate_coordinate("longitude", cafe_basic_info_data, -180, 180)

    latitude = cafe_basic_info_data["latitude"]
    longitude = cafe_basic_info_data["longitude"]

    if "latitude" not in errors and "longitude" not in errors and (latitude is None) != (longitude is None):
        errors["coordinates"] = "Latitude and longitude must be provided together."

    cafe_basic_info_data["user_id"] = 1

    return errors, cafe_basic_info_data

def validate_cafe_features_data(cafe_features_data):
    errors = {}

    if not isinstance(cafe_features_data, dict):
        errors["features"] = "Cafe features data must be an object."
        return errors, None

    # =================== WIFI ======================
    errors |= validate_choice("wifi_quality", cafe_features_data, "wifi quality", WifiQuality)

    # ================ POWER-OUTLETS ================
    errors |= validate_choice("power_outlets", cafe_features_data, "power outlets", PowerOutlets)

    # ================ NOISE-LEVEL ================
    errors |= validate_choice("noise_level", cafe_features_data, "noise level", NoiseLevel)

    # ================ SEATING ================
    errors |= validate_choice("seating_type", cafe_features_data, "seating type", Seating)

    # ================ AIR-CONDITIONING ================
    errors |= validate_choice("air_conditioning", cafe_features_data, "air conditioning", AirConditioning)

    # ================ TYPICAL_OCCUPANCY ================
    errors |= validate_choice("typical_occupancy", cafe_features_data, "typical occupancy", TypicalOccupancy)

    # ================ FOOD-OPTIONS ================
    errors |= validate_choice("food_options", cafe_features_data, "food options", FoodOptions)

    # ================ VEGETARIAN-OPTIONS ================
    errors |= validate_choice("vegetarian_options", cafe_features_data, "vegetarian options", VegetarianOptions)

    # ================ CARD-PAYMENT ================
    errors |= validate_choice("card_payment", cafe_features_data, "card payment", CardPayment)

    return errors, cafe_features_data

def validate_cafe_opening_hours_data(cafe_opening_hours_data):
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

        day_data["status"] = cafe_day_status

        cafe_day_intervals = day_data.get("intervals")
        if cafe_day_intervals is None:
            errors[
                f"opening_hours_{day_name}_interval"] = f"Opening hours intervals for {day_name.capitalize()} are required (use an empty list [] if closed)."
            continue

        if not isinstance(cafe_day_intervals, list):
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be a list."
            continue

        if cafe_day_status is not OpeningDayStatus.OPEN and cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be empty when the café is not open."
            continue

        if cafe_day_status is not OpeningDayStatus.OPEN:
            continue

        if not cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_interval"] = f"Opening hours intervals for {day_name.capitalize()} are required when the café is open."
            continue

        if len(cafe_day_intervals) > 2:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} can contain at most two intervals."
            continue

        previous_close_time = None

        for interval in cafe_day_intervals:
            if not isinstance(interval, dict):
                errors[
                    f"opening_hours_{day_name}_interval"] = f"Opening hours interval for {day_name.capitalize()} must be an object."
                continue

            if set(interval.keys()) != {"open", "close"}:
                errors[
                    f"opening_hours_{day_name}_interval"] = f"Opening hours interval for {day_name.capitalize()} must contain only 'open' and 'close'."
                continue

            open_time_text = interval["open"]
            close_time_text = interval["close"]

            if not isinstance(open_time_text, str) or not isinstance(close_time_text, str):
                errors[
                    f"opening_hours_{day_name}_time_interval"] = f"Opening and closing times for {day_name.capitalize()} must be strings."
                continue

            if not TIME_TEXT_PATTERN.fullmatch(open_time_text) or not TIME_TEXT_PATTERN.fullmatch(close_time_text):
                errors[
                    f"opening_hours_{day_name}_interval"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue

            try:
                open_time = datetime.strptime(open_time_text, TIME_FORMAT).time()
                close_time = datetime.strptime(close_time_text, TIME_FORMAT).time()
            except ValueError:
                errors[
                    f"opening_hours_{day_name}_interval"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue
            else:
                if previous_close_time is not None and open_time < previous_close_time:
                    errors[
                        f"opening_hours_{day_name}_interval"] = f"Opening intervals for {day_name.capitalize()} must not overlap."
                    continue
                interval['open'] = open_time
                interval['close'] = close_time

                previous_close_time = close_time

    return errors, cafe_opening_hours_data

def validate_cafe_review_data(cafe_review_data):
    errors = {}

    if not isinstance(cafe_review_data, dict):
        errors["cafe_review"] = "Cafe review data must be an object."
        return errors, None

    # =================== CAFE-RATING ======================
    cafe_rating = cafe_review_data.get("rating")

    if cafe_rating is None:
        errors["cafe_rating"] = "Cafe rating is required."

    elif not isinstance(cafe_rating, str):
        errors["cafe_rating"] = "Cafe rating must be a text."

    else:
        try:
            cafe_rating = Rating(cafe_rating)
        except ValueError:
            errors["cafe_rating"] = f"Invalid data! Please choose one of the options."
        else:
            cafe_review_data["rating"] = cafe_rating

    # =================== CAFE-REVIEW ======================
    cafe_review = cafe_review_data.get("text")

    if cafe_review is not None:
        if not isinstance(cafe_review, str):
            errors["cafe_review"] = "Cafe review must be a text."
        else:
            cafe_review = cafe_review.strip()

            if cafe_review:
                if len(cafe_review) > 2048:
                    errors["cafe_review"] = "Cafe review must contain at most 2048 characters."
                else:
                    cafe_review_data["text"] = cafe_review
            else:
                cafe_review_data["text"] = None

    cafe_review_data["user_id"] = 1

    return errors, cafe_review_data

def validate_cafe_photos(cafe_photos):
    errors = {}

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
                    ValueError,): errors.setdefault(error_key, []).append("The uploaded file is not a valid image.")

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