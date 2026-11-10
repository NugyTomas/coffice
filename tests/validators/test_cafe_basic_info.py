import copy

import pytest

from app.enums import CoffeeQuality, CafePrice
from app.validators.suggestions import validate_cafe_basic_info_data
from tests.validators.helpers import (assert_valid_field,
                                      assert_invalid_field,
                                      VALID_VALUES_FOR_OPTIONAL_FIELDS,
                                      INVALID_DATA_TYPES,
                                      INVALID_VALUES_FOR_REQUIRED_FIELDS
                                      )

INVALID_CHOICE_VALUES = [
    "invalid",
    "UNKNOWN",
    *INVALID_VALUES_FOR_REQUIRED_FIELDS
]

TEXT_FIELD_LIMITS = {
    "name": (2, 50),
    "address": (3, 100),
    "city": (2, 50),
}

EXTERNAL_ID_MAX_INPUT = 255 * "a"

EMAIL_MAX_INPUT = "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 53 + ".com"
EMAIL_TOO_LONG_INPUT = "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 54 + ".com"
assert len(EMAIL_MAX_INPUT) == 250
assert len(EMAIL_TOO_LONG_INPUT) == 251

WEBSITE_MAX_INPUT = "https://" + "a" * 2036 + ".com"
WEBSITE_TOO_LONG_INPUT = "https://" + "a" * 2037 + ".com"
assert len(WEBSITE_MAX_INPUT) == 2048
assert len(WEBSITE_TOO_LONG_INPUT) == 2049

INSTAGRAM_MAX_INPUT = "a" * 30
INSTAGRAM_TOO_LONG_INPUT = "a" * 31

COORDINATE_LIMITS = {
    "latitude": (-90, 90),
    "longitude": (-180, 180),
}

CHOICE_FIELDS = [
    ("price_level", CafePrice),
    ("coffee_quality", CoffeeQuality),
]
CHOICE_FIELD_NAMES = [field for field, _ in CHOICE_FIELDS]


# =================== VALIDATION_TESTS ======================
def test_valid_cafe_has_no_errors(valid_suggestion):
    errors, cleaned = validate_cafe_basic_info_data(copy.deepcopy(valid_suggestion["cafe"]))
    assert errors == {}
    assert cleaned is not None


def test_unknown_fields_are_not_in_cleaned(valid_suggestion):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data.update({"id": 999, "status": "approved", "submitted_by_id": 42})

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert not {"id", "status", "submitted_by_id"} & cleaned.keys()


def test_invalid_cafe_data_type():
    errors, cleaned = validate_cafe_basic_info_data("text")

    assert "cafe" in errors
    assert cleaned is None


# depends on the optional-fields rule
def test_missing_optional_field(valid_suggestion):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data.pop("website")

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert errors == {}
    assert "website" not in cleaned


# =================== EXTERNAL_PLACE_ID ======================
@pytest.mark.parametrize("raw, expected", [
    pytest.param(
        EXTERNAL_ID_MAX_INPUT,
        EXTERNAL_ID_MAX_INPUT,
        id="external-id-max-length"
    ),
    pytest.param(
        f"  {EXTERNAL_ID_MAX_INPUT}  ",
        EXTERNAL_ID_MAX_INPUT,
        id="external-id-max-length-with-whitespace"
    ),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_external_place_id(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "external_place_id", raw, expected)


@pytest.mark.parametrize("raw", [
    pytest.param({EXTERNAL_ID_MAX_INPUT}, id="external-id-too-long"),
    *INVALID_DATA_TYPES
])
def test_invalid_external_place_id(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "external_place_id", raw)


# =================== NAME, ADDRESS, CITY ======================
def valid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        max_length_text = "a" * max_len

        yield from [
            (field, "Kavárna Šnek", "Kavárna Šnek"),
            (field, "Test", "Test"),
            (field, "a" * min_len, "a" * min_len),
            pytest.param(
                field,
                max_length_text,
                max_length_text,
                id=f"{field}-max-length"
            ),
            pytest.param(
                field,
                f"  {max_length_text}  ",
                max_length_text,
                id=f"{field}-max-length-with-whitespace"
            ),
        ]


@pytest.mark.parametrize("field, raw, expected", list(valid_text_cases()))
def test_valid_text_fields_validation(valid_suggestion, field, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw, expected)


def invalid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        min_length_text = "a" * (min_len - 1)
        max_length_text = "a" * (max_len + 1)

        yield from [
            pytest.param(
                field,
                f"  {min_length_text}  ",
                id=f"{field}-below-min-length"
            ),
            pytest.param(
                field,
                f"  {max_length_text}  ",
                id=f"{field}-above-max-length"
            ),
            *((field, value) for value in INVALID_VALUES_FOR_REQUIRED_FIELDS)
        ]


@pytest.mark.parametrize("field, raw", list(invalid_text_cases()))
def test_invalid_text_fields_validation(valid_suggestion, field, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw)


@pytest.mark.parametrize("field", ["address", "city"])
def test_address_and_city_require_letter(valid_suggestion, field):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, "12345")


# =================== POSTAL_CODE ======================
@pytest.mark.parametrize("raw, expected", [
    ("123 45", "123 45"),
    ("  123 45  ", "123 45")
])
def test_valid_postal_code_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "postal_code", raw, expected)


@pytest.mark.parametrize("raw", [
    "12345",
    *INVALID_VALUES_FOR_REQUIRED_FIELDS
])
def test_invalid_postal_code_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "postal_code", raw)


# =================== PHONE ======================
@pytest.mark.parametrize("raw, expected", [
    ("123 456 789", "+420 123 456 789"),
    ("  123 456 789  ", "+420 123 456 789"),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_phone_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "phone", raw, expected)


@pytest.mark.parametrize("raw", [
    "+420 123 456 789",
    "123 465 789 7",
    "123456789",
    "abc",
    *INVALID_DATA_TYPES
])
def test_invalid_phone_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "phone", raw)


# =================== EMAIL ======================
@pytest.mark.parametrize("raw, expected", [
    ("test@example.com", "test@example.com"),
    ("  test@example.com  ", "test@example.com"),
    ("test@sub.example.com", "test@sub.example.com"),
    ("test+coffee@example.com", "test+coffee@example.com"),
    ("TEST@EXAMPLE.COM", "TEST@example.com"),
    pytest.param(
        EMAIL_MAX_INPUT,
        EMAIL_MAX_INPUT,
        id="email-max-length"
    ),
    pytest.param(
        f"  {EMAIL_MAX_INPUT}  ",
        EMAIL_MAX_INPUT,
        id="email-max-length-with-whitespace"
    ),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_email_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "email", raw, expected)


@pytest.mark.parametrize("raw", [
    "invalid-email",
    "test@",
    "test@example",
    "@example.com",
    pytest.param(EMAIL_TOO_LONG_INPUT, id="email-too-long"),
    *INVALID_DATA_TYPES
])
def test_invalid_email_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "email", raw)


# =================== WEBSITE ======================
@pytest.mark.parametrize("raw, expected", [
    ("example.com", "https://example.com"),
    ("  example.com  ", "https://example.com"),
    ("http://example.com", "https://example.com"),
    ("https://example.com", "https://example.com"),
    ("example.com/about", "https://example.com/about"),
    ("example.co.uk", "https://example.co.uk"),
    ("HTTPS://EXAMPLE.COM", "https://EXAMPLE.COM"),
    pytest.param(
        WEBSITE_MAX_INPUT,
        WEBSITE_MAX_INPUT,
        id="website-max-length"
    ),
    pytest.param(
        f"  {WEBSITE_MAX_INPUT}  ",
        WEBSITE_MAX_INPUT,
        id="website-max-length-with-whitespace"
    ),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_website_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "website", raw, expected)


@pytest.mark.parametrize("raw", [
    "not-a-website",
    "example",
    "https://",
    pytest.param(WEBSITE_TOO_LONG_INPUT, id="website-too-long"),
    *INVALID_DATA_TYPES
])
def test_invalid_website_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "website", raw)


# =================== INSTAGRAM ======================
@pytest.mark.parametrize("raw, expected", [
    ("example", "@example"),
    ("@example", "@example"),
    ("  @example  ", "@example"),
    ("Cafe", "@cafe"),
    ("@Example_cafe123", "@example_cafe123"),
    ("example.cafe", "@example.cafe"),
    ("example.cafe_123", "@example.cafe_123"),
    (INSTAGRAM_MAX_INPUT, "@" + INSTAGRAM_MAX_INPUT),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_instagram_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "instagram", raw, expected)


@pytest.mark.parametrize("raw", [
    "@@cafe",
    ".cafe",
    "cafe.",
    "cafe..name",
    "cafe-name",
    "cafe name",
    "cafe/name",
    pytest.param(INSTAGRAM_TOO_LONG_INPUT, id="username-too-long"),
    *INVALID_DATA_TYPES
])
def test_invalid_instagram_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], "instagram", raw)


# =================== LATITUDE, LONGITUDE ======================
def valid_coordinate_cases():
    for field, (min_limit, max_limit) in COORDINATE_LIMITS.items():
        valid_value = 49.74 if field == "latitude" else 13.37
        yield from [
            (field, min_limit, float(min_limit)),
            (field, max_limit, float(max_limit)),
            (field, 0, 0.0),
            (field, valid_value, valid_value),
        ]


@pytest.mark.parametrize("field, raw, expected", list(valid_coordinate_cases()))
def test_valid_coordinates_validation(valid_suggestion, field, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw, expected)


def invalid_coordinate_cases():
    for field, (min_limit, max_limit) in COORDINATE_LIMITS.items():
        yield from [
            (field, "49.74"),
            (field, min_limit - 0.01),
            (field, max_limit + 0.01),
            *((field, value) for value in INVALID_DATA_TYPES),
            (field, float("nan")),
            (field, float("inf")),
            (field, float("-inf"))
        ]


@pytest.mark.parametrize("field, raw", list(invalid_coordinate_cases()))
def test_invalid_coordinates_validation(valid_suggestion, field, raw):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw)


# =================== PRICE-LEVEL, COFFEE-QUALITY ======================
@pytest.mark.parametrize("raw, expected", [
    ("unknown", "unknown"),
    ("low", "low"),
    ("  low  ", "low"),
    ("medium", "medium"),
    ("high", "high"),
])
@pytest.mark.parametrize("field, enum_class", CHOICE_FIELDS)
def test_valid_choices_validation(valid_suggestion, field, enum_class, raw, expected):
    assert_valid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw, enum_class(expected))


@pytest.mark.parametrize("raw", INVALID_CHOICE_VALUES)
@pytest.mark.parametrize("field", CHOICE_FIELD_NAMES)
def test_invalid_choices_validation(valid_suggestion, raw, field):
    assert_invalid_field(validate_cafe_basic_info_data, valid_suggestion["cafe"], field, raw)
