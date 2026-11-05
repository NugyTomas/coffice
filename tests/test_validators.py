import copy
from app.validators.suggestions import validate_cafe_basic_info_data

import pytest

TEXT_FIELD_LIMITS = {
    "name": (2, 50),
    "address": (3, 100),
    "city": (2, 50),
}


@pytest.mark.parametrize("field, raw, expected", [
    ("name", "  My Cafe  ", "My Cafe"),
    ("address", "  U Letiste 2  ", "U Letiste 2"),
    ("city", "  Pilsen  ", "Pilsen"),
    ("postal_code", "  123 45  ", "123 45"),
])
def test_cafe_fields_are_stripped(valid_suggestion, field, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field not in errors
    assert cleaned[field] == expected


def valid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        yield from [
            (field, "a" * min_len, "a" * min_len),
            (field, "a" * max_len, "a" * max_len)
        ]


@pytest.mark.parametrize("field, raw, expected", list(valid_text_cases()))
def test_valid_text_fields_validation(valid_suggestion, field, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field not in errors
    assert cleaned[field] == expected


def invalid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        yield from [
            (field, None),
            (field, ""),
            (field, "  "),
            (field, 123),
            (field, "a" * (min_len - 1)),
            (field, "a" * (max_len + 1)),
        ]


@pytest.mark.parametrize("field, raw", list(invalid_text_cases()))
def test_invalid_text_fields_validation(valid_suggestion, field, raw):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field in errors
    assert field not in cleaned


@pytest.mark.parametrize("field", ["address", "city"])
def test_address_and_city_require_letter(valid_suggestion, field):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = "12345"

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field in errors
    assert field not in cleaned


def test_valid_postal_code_validation(valid_suggestion):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["postal_code"] = "123 45"

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "postal_code" not in errors
    assert cleaned["postal_code"] == "123 45"


@pytest.mark.parametrize("raw", [
    None,
    "",
    "  ",
    "12345",
    12345])
def test_invalid_postal_code_validation(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["postal_code"] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "postal_code" in errors
    assert "postal_code" not in cleaned
