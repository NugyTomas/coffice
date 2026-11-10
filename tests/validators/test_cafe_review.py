from datetime import datetime
import copy

import pytest

from app.validators.suggestions import validate_cafe_review_data
from tests.conftest import valid_suggestion
from tests.validators.helpers import (assert_valid_field,
                                      assert_invalid_field,
                                      VALID_VALUES_FOR_OPTIONAL_FIELDS,
                                      INVALID_VALUES_FOR_REQUIRED_FIELDS, INVALID_DATA_TYPES)

REVIEW_TEXT_MAX_INPUT = "a" * 2048
REVIEW_TOO_LONG_INPUT = "a" * 2049


# =================== VALIDATION_TESTS ======================
def test_valid_cafe_review_has_no_errors(valid_suggestion):
    errors, cleaned = validate_cafe_review_data(copy.deepcopy(valid_suggestion["cafe_review"]))
    assert errors == {}
    assert cleaned is not None


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
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    ("1", 1),
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
    (" 5 ", 5),
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


# =================== CAFE-REVIEW ======================
@pytest.mark.parametrize("raw, expected", [
    ("  Great coffee!  ", "Great coffee!"),
    pytest.param(
        REVIEW_TEXT_MAX_INPUT,
        REVIEW_TEXT_MAX_INPUT,
        id="review-text-max-length"),
    pytest.param(
        f"  {REVIEW_TEXT_MAX_INPUT}  ",
        REVIEW_TEXT_MAX_INPUT,
        id="review-text-max-length-with-whitespace"),
    *VALID_VALUES_FOR_OPTIONAL_FIELDS
])
def test_valid_review_text_validation(valid_suggestion, raw, expected):
    assert_valid_field(validate_cafe_review_data, valid_suggestion["cafe_review"], "text", raw, expected)


@pytest.mark.parametrize("raw", [
    pytest.param(REVIEW_TOO_LONG_INPUT, id="review-text-too-long"),
    *INVALID_DATA_TYPES,
])
def test_invalid_review_text_validation(valid_suggestion, raw):
    assert_invalid_field(validate_cafe_review_data, valid_suggestion["cafe_review"], "text", raw)
