import copy

import pytest

from app.enums import CoffeeQuality, CafePrice
from app.validators.suggestions import validate_cafe_basic_info_data

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


def prepare_cafe_data(valid_suggestion, field, raw):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    return data


def assert_valid_field(valid_suggestion, field, raw, expected):
    data = prepare_cafe_data(valid_suggestion, field, raw)
    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field not in errors
    assert cleaned.get(field) == expected


def assert_invalid_field(valid_suggestion, field, raw):
    data = prepare_cafe_data(valid_suggestion, field, raw)
    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field in errors
    assert field not in cleaned


# =================== EXTERNAL_PLACE_ID ======================
@pytest.mark.parametrize("raw, expected", [
    (EXTERNAL_ID_MAX_INPUT, EXTERNAL_ID_MAX_INPUT),
    (f"  {EXTERNAL_ID_MAX_INPUT}  ", EXTERNAL_ID_MAX_INPUT),
    ("", None),
    ("  ", None),
    (None, None),
])
def test_valid_external_place_id(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "external_place_id", raw, expected)


@pytest.mark.parametrize("raw", [
    {},
    [],
    True,
    False,
    f"a{EXTERNAL_ID_MAX_INPUT}",
    123
])
def test_invalid_external_place_id(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "external_place_id", raw)


# =================== NAME, ADDRESS, CITY ======================
def valid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        max_length_text = "a" * max_len

        yield from [
            (field, "Test", "Test"),
            (field, "a" * min_len, "a" * min_len),
            (field, max_length_text, max_length_text),
            (field, f"  {max_length_text}  ", max_length_text),
        ]


@pytest.mark.parametrize("field, raw, expected", list(valid_text_cases()))
def test_valid_text_fields_validation(valid_suggestion, field, raw, expected):
    assert_valid_field(valid_suggestion, field, raw, expected)


def invalid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        min_length_text = "a" * (min_len - 1)
        max_length_text = "a" * (max_len + 1)
        yield from [
            (field, None),
            (field, ""),
            (field, "  "),
            (field, []),
            (field, {}),
            (field, True),
            (field, False),
            (field, 123),
            (field, f"  {min_length_text}  "),
            (field, f"  {max_length_text}  ")
        ]


@pytest.mark.parametrize("field, raw", list(invalid_text_cases()))
def test_invalid_text_fields_validation(valid_suggestion, field, raw):
    assert_invalid_field(valid_suggestion, field, raw)


@pytest.mark.parametrize("field", ["address", "city"])
def test_address_and_city_require_letter(valid_suggestion, field):
    assert_invalid_field(valid_suggestion, field, "12345")


# =================== POSTAL_CODE ======================
@pytest.mark.parametrize("raw, expected", [
    ("123 45", "123 45"),
    ("  123 45  ", "123 45")
])
def test_valid_postal_code_validation(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "postal_code", raw, expected)


@pytest.mark.parametrize("raw", [
    None,
    [],
    {},
    True,
    False,
    "",
    "  ",
    "12345",
    12345
])
def test_invalid_postal_code_validation(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "postal_code", raw)


# =================== PHONE ======================
@pytest.mark.parametrize("raw, expected", [
    ("", None),
    ("  ", None),
    (None, None),
    ("123 456 789", "+420 123 456 789"),
    ("  123 456 789  ", "+420 123 456 789")
])
def test_valid_phone_validation(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "phone", raw, expected)


@pytest.mark.parametrize("raw", [
    "+420 123 456 789",
    "123 465 789 7",
    "abc",
    123456789,
    [],
    {},
    True,
    False
])
def test_invalid_phone_validation(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "phone", raw)


# =================== EMAIL ======================
@pytest.mark.parametrize("raw, expected", [
    ("", None),
    ("  ", None),
    (None, None),
    ("test@example.com", "test@example.com"),
    ("  test@example.com  ", "test@example.com"),
    ("test@sub.example.com", "test@sub.example.com"),
    ("test+coffee@example.com", "test+coffee@example.com"),
    (EMAIL_MAX_INPUT, EMAIL_MAX_INPUT),
    (f"  {EMAIL_MAX_INPUT}  ", EMAIL_MAX_INPUT),
])
def test_valid_email_validation(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "email", raw, expected)


@pytest.mark.parametrize("raw", [
    "invalid-email",
    "test@",
    "test@example",
    "@example.com",
    EMAIL_TOO_LONG_INPUT,
    123,
    [],
    {},
    True,
    False
])
def test_invalid_email_validation(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "email", raw)


# =================== WEBSITE ======================
@pytest.mark.parametrize("raw, expected", [
    ("", None),
    ("  ", None),
    (None, None),
    ("example.com", "https://example.com"),
    ("  example.com  ", "https://example.com"),
    ("http://example.com", "https://example.com"),
    ("https://example.com", "https://example.com"),
    ("example.com/about", "https://example.com/about"),
    ("example.co.uk", "https://example.co.uk"),
    ("HTTPS://EXAMPLE.COM", "https://EXAMPLE.COM"),
    (WEBSITE_MAX_INPUT, WEBSITE_MAX_INPUT),
    (f"  {WEBSITE_MAX_INPUT}  ", WEBSITE_MAX_INPUT),
])
def test_valid_website_validation(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "website", raw, expected)


@pytest.mark.parametrize("raw", [
    "not-a-website",
    "example",
    "https://",
    WEBSITE_TOO_LONG_INPUT,
    123,
    [],
    {},
    True,
    False
])
def test_invalid_website_validation(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "website", raw)


# =================== INSTAGRAM ======================
@pytest.mark.parametrize("raw, expected", [
    ("", None),
    ("  ", None),
    (None, None),
    ("example", "@example"),
    ("@example", "@example"),
    ("  @example  ", "@example"),
    ("Cafe", "@cafe"),
    ("@Example_cafe123", "@example_cafe123"),
    ("example.cafe", "@example.cafe"),
    ("example.cafe_123", "@example.cafe_123"),
    (INSTAGRAM_MAX_INPUT, "@" + INSTAGRAM_MAX_INPUT),
])
def test_valid_instagram_validation(valid_suggestion, raw, expected):
    assert_valid_field(valid_suggestion, "instagram", raw, expected)


@pytest.mark.parametrize("raw", [
    "@@cafe",
    ".cafe",
    "cafe.",
    "cafe..name",
    "cafe-name",
    "cafe name",
    "cafe/name",
    INSTAGRAM_TOO_LONG_INPUT,
    123,
    [],
    {},
    True,
    False
])
def test_invalid_instagram_validation(valid_suggestion, raw):
    assert_invalid_field(valid_suggestion, "instagram", raw)


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
    assert_valid_field(valid_suggestion, field, raw, expected)


def invalid_coordinate_cases():
    for field, (min_limit, max_limit) in COORDINATE_LIMITS.items():
        yield from [
            (field, ""),
            (field, "  "),
            (field, None),
            (field, True),
            (field, False),
            (field, "49.74"),
            (field, []),
            (field, {}),
            (field, min_limit - 0.01),
            (field, max_limit + 0.01),
        ]


@pytest.mark.parametrize("field, raw", list(invalid_coordinate_cases()))
def test_invalid_coordinates_validation(valid_suggestion, field, raw):
    assert_invalid_field(valid_suggestion, field, raw)


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
    assert_valid_field(valid_suggestion, field, raw, enum_class(expected))


@pytest.mark.parametrize("raw", [
    "",
    "  ",
    None,
    "invalid",
    "LOW",
    123,
    [],
    {},
    True,
    False
])
@pytest.mark.parametrize("field", [
    "price_level",
    "coffee_quality"
])
def test_invalid_choices_validation(valid_suggestion, raw, field):
    assert_invalid_field(valid_suggestion, field, raw)
