import copy


import pytest


from app.validators.suggestions import validate_cafe_basic_info_data


TEXT_FIELD_LIMITS = {
    "name": (2, 50),
    "address": (3, 100),
    "city": (2, 50),
}
EXTERNAL_ID_MAX_INPUT = 255 * "a"


# =================== EXTERNAL_PLACE_ID ======================
@pytest.mark.parametrize("raw, expected", [
    (EXTERNAL_ID_MAX_INPUT, EXTERNAL_ID_MAX_INPUT),
    (f"  {EXTERNAL_ID_MAX_INPUT}  ", EXTERNAL_ID_MAX_INPUT),
    ("", None),
    ("  ", None),
    (None, None),
])
def test_valid_external_place_id(valid_suggestion, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["external_place_id"] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "external_place_id" not in errors
    assert cleaned.get("external_place_id") == expected


@pytest.mark.parametrize("raw", [
    {},
    [],
    f"a{EXTERNAL_ID_MAX_INPUT}",
    123
])
def test_invalid_external_place_id(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data["external_place_id"] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert "external_place_id" in errors
    assert "external_place_id" not in cleaned


# =================== NAME, ADDRESS, CITY ======================
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
        min_length_text = "a" * (min_len - 1)
        max_length_text = "a" * (max_len + 1)
        yield from [
            (field, None),
            (field, ""),
            (field, "  "),
            (field, 123),
            (field, f"  {min_length_text}  "),
            (field, f"  {max_length_text}  ")
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


# =================== POSTAL_CODE ======================
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
