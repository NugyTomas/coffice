import copy
from app.validators.suggestions import validate_cafe_basic_info_data

import pytest

@pytest.mark.parametrize("field, raw, expected", [
    ("name", "a"*2, "a"*2),
    ("name", "a"*50, "a"*50),
    ("address", "a"*3, "a"*3),
    ("address", "a"*100, "a"*100),
    ("city", "a"*2, "a"*2),
    ("city", "a"*50, "a"*50),
])
def test_text_field_valid_validation(valid_suggestion, field, raw, expected):
    data = copy.deepcopy(valid_suggestion["cafe"])
    data[field] = raw

    errors, cleaned = validate_cafe_basic_info_data(data)

    assert field not in errors
    assert cleaned [field] == expected