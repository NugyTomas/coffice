import copy

import pytest

from app.enums import (WifiQuality,
                       PowerOutlets,
                       NoiseLevel,
                       Seating,
                       AirConditioning,
                       TypicalOccupancy,
                       FoodOptions,
                       VegetarianOptions,
                       CardPayment)

from app.validators.suggestions import validate_cafe_features_data
from tests.validators.helpers import assert_valid_field

WIFI_QUALITY_VALUES = [
    "unknown",
    "unavailable",
    "slow",
    "stable",
    "fast",
]

POWER_OUTLETS_VALUES = [
    "unknown",
    "unavailable",
    "limited",
    "everywhere"
]

NOISE_LEVEL_VALUES = [
    "unknown",
    "noisy",
    "moderate",
    "quiet"
]

SEATING_VALUES = [
    "unknown",
    "unavailable",
    "bar-like",
    "casual",
    "work-friendly"
]

AIR_CONDITIONING_VALUES = [
    "unknown",
    "no",
    "yes"
]

TYPICAL_OCCUPANCY_VALUES = [
    "unknown",
    "low",
    "moderate",
    "busy"
]

FOOD_OPTIONS_VALUES = [
    "unknown",
    "unavailable",
    "snacks",
    "good-variety"
]

VEGETARIAN_OPTIONS_VALUES = [
    "unknown",
    "unavailable",
    "snacks",
    "good-variety"
]

CARD_PAYMENT_VALUES = [
    "unknown",
    "yes",
    "no"
]


# Invalid choice values are tested in test_cafe_basic_info.py
# because all choice fields use the same validate_choice() helper.

# =================== VALIDATION_TESTS ======================
def test_valid_features_has_no_errors(valid_suggestion):
    errors, cleaned = validate_cafe_features_data(copy.deepcopy(valid_suggestion["cafe_features"]))

    assert errors == {}
    assert cleaned is not None


def test_unknown_fields_are_not_in_cleaned(valid_suggestion):
    data = copy.deepcopy(valid_suggestion["cafe_features"])
    data.update({"id": 999, "cafe_id": "test123"})

    errors, cleaned = validate_cafe_features_data(data)

    assert not {"id", "cafe_id"} & cleaned.keys()


def test_invalid_cafe_data_type():
    errors, cleaned = validate_cafe_features_data("name")

    assert "features" in errors
    assert cleaned is None


# =================== WIFI-QUALITY ======================
@pytest.mark.parametrize("raw", WIFI_QUALITY_VALUES)
def test_valid_wifi_quality_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "wifi_quality",
                       raw,
                       WifiQuality(raw))


# =================== POWER-OUTLETS ======================
@pytest.mark.parametrize("raw", POWER_OUTLETS_VALUES)
def test_valid_power_outlets_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "power_outlets",
                       raw,
                       PowerOutlets(raw))


# ================ NOISE-LEVEL ================
@pytest.mark.parametrize("raw", NOISE_LEVEL_VALUES)
def test_valid_noise_level_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "noise_level",
                       raw,
                       NoiseLevel(raw))


# ================ SEATING ================
@pytest.mark.parametrize("raw", SEATING_VALUES)
def test_valid_seating_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "seating_type",
                       raw,
                       Seating(raw))


# ================ AIR-CONDITIONING ================
@pytest.mark.parametrize("raw", AIR_CONDITIONING_VALUES)
def test_valid_air_conditioning_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "air_conditioning",
                       raw,
                       AirConditioning(raw))


# ================ TYPICAL_OCCUPANCY ================
@pytest.mark.parametrize("raw", TYPICAL_OCCUPANCY_VALUES)
def test_valid_typical_occupancy_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "typical_occupancy",
                       raw,
                       TypicalOccupancy(raw))


# ================ FOOD-OPTIONS ================
@pytest.mark.parametrize("raw", FOOD_OPTIONS_VALUES)
def test_valid_food_options_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "food_options",
                       raw,
                       FoodOptions(raw))


# ================ VEGETARIAN-OPTIONS ================
@pytest.mark.parametrize("raw", VEGETARIAN_OPTIONS_VALUES)
def test_valid_vegetarian_options_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "vegetarian_options",
                       raw,
                       VegetarianOptions(raw))


# ================ CARD-PAYMENT ================
@pytest.mark.parametrize("raw", CARD_PAYMENT_VALUES)
def test_valid_card_payment_options_validation(valid_suggestion, raw):
    assert_valid_field(validate_cafe_features_data,
                       valid_suggestion["cafe_features"],
                       "card_payment",
                       raw,
                       CardPayment(raw))
