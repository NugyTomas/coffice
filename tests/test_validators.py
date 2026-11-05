import copy
from app.validators.suggestions import validate_cafe_basic_info_data

import pytest

TEXT_FIELD_LIMITS = {
    "name": (2, 50),
    "address": (3, 100),
    "city": (2, 50),
}

def valid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        yield from [
            (field, "a" * min_len, "a" * min_len),
            (field, "a" * max_len, "a" * max_len)
        ]

@pytest.mark.parametrize("field, raw, expected", list(valid_text_cases()))
def test_text_field_valid_validation(valid_suggestion, field, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field not in errors
    assert cleaned[field] == expected


def invalid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        yield from [
            (field, ""),
            (field, "  "),
            (field, None),
            (field, 123),
            (field, "a" * (min_len - 1)),
            (field, "a" * (max_len + 1)),
        ]

@pytest.mark.parametrize("field, raw", list(invalid_text_cases()))
def test_text_field_invalid_validation(valid_suggestion, field, raw):
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