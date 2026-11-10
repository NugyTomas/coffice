from datetime import datetime
import copy

import pytest

from app.validators.suggestions import validate_cafe_review_data
from tests.conftest import valid_suggestion
from tests.validators.helpers import (assert_valid_field,
                                      assert_invalid_field,
                                      INVALID_VALUES_FOR_REQUIRED_FIELDS)


# =================== VALIDATION_TESTS ======================
def test_valid_cafe_has_no_errors(valid_suggestion):
    errors, cleaned = validate_cafe_review_data(copy.deepcopy(valid_suggestion["cafe_review"]))
    assert errors == {}


def test_unknown_fields_are_not_in_cleaned(valid_suggestion):
    data = copy.deepcopy(valid_suggestion["cafe_review"])
    data.update({"id": 999, "cafe_id": 999, "submitted_by_id": 42, "created_at": datetime.now()})

    errors, cleaned = validate_cafe_review_data(data)

    assert not {"id", "cafe_id", "submitted_by_id", "created_at"} & cleaned.keys()


def test_invalid_cafe_data_type():
    errors, cleaned = validate_cafe_review_data("text")

    assert "cafe_review" in errors
    assert cleaned is None


# =================== CAFE-RATING ======================
@pytest.mark.parametrize("raw, expected", [
    ("1", 1),
    (5, 5),
    (" 5 ", 5)
])
def test_valid_cafe_rating_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_review_data, valid_suggestion["cafe_review"], "rating", raw, expected)


@pytest.mark.parametrize("raw", [
    0,
    6,
    " 6 ",
    3.5,
    4.0,
    *INVALID_VALUES_FOR_REQUIRED_FIELDS
])
def test_invalid_cafe_rating_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_review_data, valid_suggestion["cafe_review"], "rating", raw)

