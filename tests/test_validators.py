import copy

import pytest


from app.validators.suggestions import validate_cafe_basic_info_data



TEXT_FIELD_LIMITS = {
    "name": (2, 50),
    "address": (3, 100),
    "city": (2, 50),
}


def valid_text_cases():
    for field, (min_len, max_len) in TEXT_FIELD_LIMITS.items():
        max_length_text = "a" * max_len

        yield from [
            (field, "a" * min_len, "a" * min_len),
            (field, max_length_text, max_length_text),
            (field, f"  {max_length_text}  ", max_length_text),
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


@pytest.mark.parametrize("raw, expected", [
    ("123 45", "123 45"),
    ("  123 45  ", "123 45")
])
def test_valid_postal_code_validation(valid_suggestion, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["postal_code"] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "postal_code" not in errors
    assert cleaned["postal_code"] == expected


@pytest.mark.parametrize("raw", [
    None,
    "",
    "  ",
    "12345",
    12345
])
def test_invalid_postal_code_validation(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["postal_code"] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "postal_code" in errors
    assert "postal_code" not in cleaned
