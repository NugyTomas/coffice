from app.enums import (WifiQuality,
                       PowerOutlets,
                       NoiseLevel,
                       Seating,
                       AirConditioning,
                       TypicalOccupancy,
                       FoodOptions,
                       VegetarianOptions,
                       CardPayment
                       )
from app.validators.common import validate_choice


# =================== MAIN FUNCTION ======================
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

    for name, label, enum in feature_fields:
        choice_errors, value = validate_choice(name, cafe_features_data, label, enum)
        errors |= choice_errors

        if not choice_errors:
            cleaned[name] = value

    return errors, cleaned
