import re
from email_validator import validate_email, EmailNotValidError

from flask import Flask, render_template, request, jsonify
import json
from extensions import db
from models import (Cafe, OpeningHours, CafePhoto, CafeFeature, User, Review,
                    CafeSuggestion, CafeSuggestionOpeningHours, CafeSuggestionPhoto, CafeSuggestionFeature,
                    CafeSuggestionReview)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coffice.db"
db.init_app(app)

with app.app_context():
    db.create_all()


# =========================================
# ROUTES
# =========================================
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

    # errors = check_suggestion_data(suggestion_json, photos)
    #
    errors = {}

    if not suggestion_json:
        errors["suggestion"] = "Missing suggestion data."
        return errors

    try:
        cafe_suggestion = json.loads(suggestion_json)
    except json.JSONDecodeError:
        errors["suggestion"] = "Invalid JSON data."
        return errors

    if not cafe_suggestion:
        errors["suggestion"] = "Empty suggestion data."
        return errors

    # =========================================
    # CAFE_SUGGESTION_DATA
    # =========================================
    cafe_data = cafe_suggestion.get("cafe")

    if not isinstance(cafe_data, dict):
        errors["cafe"] = "Cafe data must be an object."
    else:

        # =================== NAME ======================
        cafe_name = cafe_data.get("name")

        if not isinstance(cafe_name, str):
            errors["name"] = "Name must be a text."

        else:
            clean_name = cafe_name.strip()
            if not clean_name:
                errors["name"] = "Name cannot be empty."

            elif len(clean_name) < 2:
                errors["name"] = "Name must contain at least 2 characters."

            elif len(clean_name) > 50:
                errors["name"] = "Name must contain at most 50 characters."
            else:
                cafe_data["name"] = clean_name

        # =================== ADDRESS ======================
        cafe_address = cafe_data.get("address")

        if not isinstance(cafe_address, str):
            errors["address"] = "Address must be a text."

        else:
            clean_address = cafe_address.strip()
            if not clean_address:
                errors["address"] = "Address cannot be empty."

            elif len(clean_address) < 3:
                errors["address"] = "Address must contain at least 3 characters."

            elif len(clean_address) > 100:
                errors["address"] = "Address must contain at most 100 characters."
            else:
                cafe_data["address"] = clean_address

        # =================== CITY ======================
        cafe_city = cafe_data.get("city")

        if not isinstance(cafe_city, str):
            errors["city"] = "City must be a text."
        else:
            clean_city = cafe_city.strip()

            if not clean_city:
                errors["city"] = "City cannot be empty."

            elif len(clean_city) < 2:
                errors["city"] = "City must contain at least 2 characters."

            elif len(clean_city) > 50:
                errors["city"] = "City must contain at most 50 characters."
            else:
                cafe_data["city"] = clean_city

        # =================== POSTAL CODE ======================
        cafe_postal_code = cafe_data.get("postal_code")
        if not isinstance(cafe_postal_code, str):
            errors["postal_code"] = "Postal code must be a text."

        else:
            clean_postal_code = cafe_postal_code.strip()

            if not clean_postal_code:
                errors["postal_code"] = "Postal code cannot be empty."

            elif len(clean_postal_code) != 6 or clean_postal_code[3] != " " or not clean_postal_code.replace(" ","").isdigit():
                errors["postal_code"] = "Postal code must be in format 'XXX XX'."
            else:
                cafe_data["postal_code"] = clean_postal_code


        # =================== PHONE NUMBER ======================
        cafe_phone_number = cafe_data.get("phone")

        if cafe_phone_number is not None:
            if not isinstance(cafe_phone_number, str):
                errors["phone_number"] = "Phone number must be a text."
            else:
                clean_cafe_phone_number = cafe_phone_number.strip()

                if clean_cafe_phone_number:
                    phone_pattern = r"\d{3} \d{3} \d{3}"

                    if not re.fullmatch(phone_pattern, clean_cafe_phone_number):
                        errors["phone_number"] = "Phone number must be in format 'XXX XXX XXX'. We will add +420 for you."
                    else:
                        cafe_data["phone"] = "+420 " + clean_cafe_phone_number
                else:
                    cafe_data["phone"] = None

        # =================== EMAIL ======================
        cafe_email = cafe_data.get("email")

        if cafe_email is not None:
            if not isinstance(cafe_email, str):
                errors["email"] = "Email must be a text."
            else:
                clean_cafe_email = cafe_email.strip()

                if clean_cafe_email:
                    try:
                        email_validator = validate_email(clean_cafe_email, check_deliverability=True)
                        cafe_data["email"] = email_validator.normalized
                    except EmailNotValidError:
                        errors["email"] = "Email is not valid."
                else:
                    cafe_data["email"] = None
        # =================== WEBSITE ======================
        cafe_website = cafe_data.get("website")

        if cafe_website is not None:
            if not isinstance(cafe_website, str):
                errors["website"] = "Website must be a text."
            else:
                cafe_website_clean = cafe_website.strip()

                if cafe_website_clean:
                    if cafe_website_clean.startswith("http://"):
                        cafe_website_clean = "https://" + cafe_website_clean[7:]
                    elif not cafe_website_clean.startswith("https://"):
                        cafe_website_clean = "https://" + cafe_website_clean

                    website_pattern = r"https://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}(/.*)?"

                    if not re.fullmatch(website_pattern, cafe_website_clean):
                        errors["website"] = "Website is not valid."
                    else:
                        cafe_data["website"] = cafe_website_clean
                else:
                    cafe_data["website"] = None

        # =================== INSTAGRAM ======================
        cafe_instagram = cafe_data.get("instagram")

        if cafe_instagram is not None:
            if not isinstance(cafe_instagram, str):
                errors["instagram"] = "Instagram name must be a text."
            else:
                cafe_instagram_clean = cafe_instagram.strip()

                if cafe_instagram_clean:
                    if cafe_instagram_clean.startswith("@"):
                        cafe_instagram_clean =  cafe_instagram_clean[1:]

                    instagram_pattern = r"[a-z0-9._]+"
                    if not re.fullmatch(instagram_pattern, cafe_instagram_clean):
                        errors["instagram"] = "Instagram username contains invalid characters."
                    elif len(cafe_instagram_clean) > 30:
                        errors["instagram"] = "Instagram username must contain at most 30 characters."
                    elif ".." in cafe_instagram_clean:
                        errors["instagram"] = "Instagram username contains consecutive dots."
                    elif cafe_instagram_clean.startswith(".") or cafe_instagram_clean.endswith("."):
                        errors["instagram"] = "Instagram username cannot start or end with a dot."
                    else:
                        cafe_data["instagram"] = "@" + cafe_instagram_clean
                else:
                    cafe_data["instagram"] = None

        # =================== PRICE_LEVEL ======================
        cafe_price_level = cafe_data.get("cafe_price")

        if not isinstance(cafe_price_level, str):
            errors["cafe_price"] = "Cafe price level must be a text."
        else:
            clean_cafe_price = cafe_price_level.strip()

            if clean_cafe_price in ("1", "2", "3", "unknown"):
                cafe_data["cafe_price"] = clean_cafe_price
            elif not clean_cafe_price:
                errors["cafe_price"] = "Cafe price level cannot be empty."
            else:
                errors["cafe_price"] = "Invalid cafe price level."

        # =================== COFFEE_QUALITY ======================
        coffee_quality = cafe_data.get("coffee_quality")

        if not isinstance(coffee_quality, str):
            errors["coffee_quality"] = "Coffee quality level must be a text."
        else:
            clean_coffee_quality = coffee_quality.strip()

            if clean_coffee_quality in ("1", "2", "3", "unknown"):
                cafe_data["coffee_quality"] = clean_coffee_quality
            elif not clean_coffee_quality:
                errors["coffee_quality"] = "Coffee quality cannot be empty."
            else:
                errors["coffee_quality"] = "Invalid coffee quality."

        # =================== LATITUDE ======================
        cafe_latitude = cafe_data.get("latitude")

        if cafe_latitude is not None:
            try:
                clean_cafe_latitude = float(cafe_latitude)
                if -90 <= clean_cafe_latitude <= 90:
                    cafe_data["latitude"] = clean_cafe_latitude
                else:
                    cafe_data["latitude"] = None
            except (TypeError, ValueError):
                cafe_data["latitude"] = None
        else:
            cafe_data["latitude"] = None

        # =================== LONGITUDE ======================
        cafe_longitude = cafe_data.get("longitude")

        if cafe_longitude is not None:
            try:
                clean_cafe_longitude = float(cafe_longitude)
                if -180 <= clean_cafe_longitude <= 180:
                    cafe_data["longitude"] = clean_cafe_longitude
                else:
                    cafe_data["longitude"] = None
            except (TypeError, ValueError):
                cafe_data["longitude"] = None
        else:
            cafe_data["longitude"] = None

    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    return jsonify({
        "success": True
    }), 201


# =========================================
# HELPER FUNCTION
# =========================================
def check_suggestion_data(suggestion_json, photos):
    pass
    # errors = {}
    #
    # if not suggestion_json:
    #     errors["suggestion"] = "Missing suggestion data."
    #     return errors
    #
    # try:
    #     cafe_suggestion = json.loads(suggestion_json)
    # except json.JSONDecodeError:
    #     errors["suggestion"] = "Invalid JSON data."
    #     return errors
    #
    # if not cafe_suggestion:
    #     errors["suggestion"] = "Empty suggestion data."
    #     return errors
    #
    # # ===================NAME======================
    #
    # cafe_data = cafe_suggestion.get("cafe")
    # print(cafe_data)

    # return errors


# =========================================
# APPLICATION ENTRY POINT
# =========================================

if __name__ == "__main__":
    app.run(debug=True)
