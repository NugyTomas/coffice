import copy
import json

import pytest

from app.validators.suggestions import check_suggestion_data, parse_suggestion_data


@pytest.mark.parametrize("raw, expected", [
    ('{"cafe": {}}', {"cafe": {}}),
    ('{"cafe": {}, "cafe_review": {"rating": 5}}', {"cafe": {}, "cafe_review": {"rating": 5}}),
])
def test_valid_parse_suggestion_data_validation(raw, expected):
    errors, cafe_suggestion = parse_suggestion_data(raw)

    assert errors == {}
    assert cafe_suggestion == expected


@pytest.mark.parametrize("raw", [
    "",
    "[]",
    "null",
    None,
    "{invalid}",
])
def test_invalid_parse_suggestion_data_validation(raw):
    errors, cafe_suggestion = parse_suggestion_data(raw)

    assert "suggestion" in errors
    assert cafe_suggestion is None


def test_valid_check_suggestion_data_validation(valid_suggestion):
    data = copy.deepcopy(valid_suggestion)
    suggestion_json = json.dumps(data)

    errors, *_ = check_suggestion_data(suggestion_json, [])

    assert errors == {}


def test_invalid_check_suggestion_data_validation(valid_suggestion):
    data = copy.deepcopy(valid_suggestion)

    del data["cafe"]["name"]
    del data["cafe_features"]["wifi_quality"]

    suggestion_json = json.dumps(data)
    errors, *_ = check_suggestion_data(suggestion_json, [])

    assert "name" in errors
    assert "wifi_quality" in errors
    assert len(errors) == 2
