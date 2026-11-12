import copy

import pytest

from app.enums import WeekDay, OpeningDayStatus
from app.validators.suggestions import validate_cafe_opening_hours_data

DAY_NAMES = [day.value for day in WeekDay]


def test_valid_opening_hours_has_no_errors(valid_suggestion):
    errors, cleaned = validate_cafe_opening_hours_data(copy.deepcopy(valid_suggestion["cafe_opening_hours"]))
    assert errors == {}
    assert cleaned is not None


def test_invalid_opening_hours_data_type():
    errors, cleaned = validate_cafe_opening_hours_data("text")

    assert "opening_hours" in errors
    assert cleaned is None


@pytest.mark.parametrize("day",
                         [
                             *DAY_NAMES
                         ])
def test_missing_opening_day(valid_suggestion, day):
    data = copy.deepcopy(valid_suggestion["cafe_opening_hours"])
    del data[day]

    errors, cleaned = validate_cafe_opening_hours_data(data)

    assert f"opening_hours_{day}" in errors
    assert day not in cleaned


@pytest.mark.parametrize("raw", [
    "open",
    None,
    []
])
def test_invalid_day_data(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe_opening_hours"])
    data["monday"] = raw

    errors, cleaned = validate_cafe_opening_hours_data(data)

    assert f"opening_hours_monday" in errors
    assert "monday" not in cleaned


@pytest.mark.parametrize("raw", [
    "oPen",
    12345,
    True,
    None,
    [],
    {}
])
def test_invalid_day_status(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe_opening_hours"])
    data["tuesday"]["status"] = raw

    errors, cleaned = validate_cafe_opening_hours_data(data)

    assert f"opening_hours_tuesday_status" in errors
    assert "tuesday" not in cleaned


@pytest.mark.parametrize("raw", [
    None,
    {},
    "Huh",
    12345,
    True,
])
def test_invalid_intervals(valid_suggestion, raw):
    data = copy.deepcopy(valid_suggestion["cafe_opening_hours"])
    data["wednesday"]["intervals"] = raw

    errors, cleaned = validate_cafe_opening_hours_data(data)

    assert f"opening_hours_wednesday_intervals" in errors
    assert cleaned["wednesday"]["status"] == OpeningDayStatus.OPEN
    assert "intervals" not in cleaned["wednesday"]
