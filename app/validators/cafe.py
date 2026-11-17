import re

from email_validator import validate_email, EmailNotValidError
from flask import current_app

from app.enums import CafePrice, CoffeeQuality

from app.validators.common import check_optional_value, validate_choice

# =========================================
# CONSTANTS
# =========================================
POSTAL_CODE_PATTERN = re.compile(r"[0-9]{3} [0-9]{2}")
PHONE_PATTERN = re.compile(r"[0-9]{3} [0-9]{3} [0-9]{3}")
WEBSITE_PATTERN = re.compile(r"https://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}(/.*)?")
INSTAGRAM_PATTERN = re.compile(r"[a-z0-9_]+(\.[a-z0-9_]+)*")


# =================== HELPERS ======================
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


def normalize_website_url(website):
    if website.lower().startswith(("http://", "https://")):
        website = website.split("://", 1)[1]

    return "https://" + website


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


# =================== MAIN FUNCTION ======================
def validate_cafe_basic_info_data(cafe_basic_info_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_basic_info_data, dict):
        errors["cafe"] = "Cafe data must be an object."
        return errors, None

    # =================== EXTERNAL_PLACE_ID ======================
    external_place_id_errors, cafe_external_id = check_optional_value("external_place_id",
                                                                      cafe_basic_info_data,
                                                                      "External ID",
                                                                      255)
    errors |= external_place_id_errors

    if not external_place_id_errors and cafe_external_id is not None:
        cleaned["external_place_id"] = cafe_external_id

    # =================== NAME, ADDRESS, CITY ======================
    required_text_fields = [
        ("name", 2, 50, False),
        ("address", 3, 100, True),
        ("city", 2, 50, True)
    ]

    for field, min_length, max_length, require_letter in required_text_fields:
        text_field_errors, value = validate_text_field(field,
                                                       cafe_basic_info_data,
                                                       min_length,
                                                       max_length,
                                                       require_letter=require_letter)

        errors |= text_field_errors

        if not text_field_errors:
            cleaned[field] = value

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
    phone_errors, cafe_phone_number = check_optional_value("phone", cafe_basic_info_data, "Phone number")
    errors |= phone_errors

    if not phone_errors and cafe_phone_number is not None:
        if not PHONE_PATTERN.fullmatch(cafe_phone_number):
            errors["phone"] = "Phone number must be in format 'XXX XXX XXX'. We will add +420 for you."

        else:
            cleaned["phone"] = "+420 " + cafe_phone_number

    # =================== EMAIL ======================
    email_errors, cafe_email = check_optional_value("email", cafe_basic_info_data, "Email", 250)
    errors |= email_errors

    if not email_errors and cafe_email is not None:
        try:
            email_validator = validate_email(cafe_email, check_deliverability=current_app.config[
                "CHECK_EMAIL_DELIVERABILITY"])
            cleaned["email"] = email_validator.normalized

        except EmailNotValidError:
            errors["email"] = "Email is not valid."

    # =================== WEBSITE ======================
    website_errors, cafe_website = check_optional_value("website", cafe_basic_info_data, "Website")
    errors |= website_errors

    if not website_errors and cafe_website is not None:
        cafe_website = normalize_website_url(cafe_website)

        if len(cafe_website) > 2048:
            errors["website"] = "Website must contain at most 2048 characters."

        elif not WEBSITE_PATTERN.fullmatch(cafe_website):
            errors["website"] = "Website is not valid."

        else:
            cleaned["website"] = cafe_website

    # =================== INSTAGRAM ======================
    instagram_errors, cafe_instagram = check_optional_value("instagram", cafe_basic_info_data, "Instagram username")
    errors |= instagram_errors

    if not instagram_errors and cafe_instagram is not None:
        cafe_instagram = cafe_instagram.lower().removeprefix("@")

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
