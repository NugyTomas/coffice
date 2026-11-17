import re

from app.validators.common import check_optional_value

# =========================================
# CONSTANTS
# =========================================
INTEGER_PATTERN = re.compile(r"[0-9]+")


# =================== MAIN FUNCTION ======================
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
