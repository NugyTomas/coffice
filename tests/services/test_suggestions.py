import json
import pytest

from app.constants import ANONYMOUS_USER_ID
from app.enums import CafeStatus
from app.services.suggestions import build_cafe_suggestion, check_for_duplicated_cafe, DuplicateCafeError
from app.validators.suggestions import validate_suggestion_data


def create_test_cafe(valid_suggestion):
    suggestion_json = json.dumps(valid_suggestion)

    (
        errors,
        basic_info,
        features,
        opening_hours,
        review,
        _photos,
    ) = validate_suggestion_data(suggestion_json, [])

    assert errors == {}

    return build_cafe_suggestion(
        basic_info,
        features,
        opening_hours,
        review,
        ANONYMOUS_USER_ID,
    )


def test_build_cafe_suggestion(valid_suggestion):
    cafe = create_test_cafe(valid_suggestion)

    assert cafe.status == CafeStatus.PENDING
    assert cafe.submitted_by_id == ANONYMOUS_USER_ID
    assert len(cafe.opening_hours) == 7
    assert cafe.features is not None
    assert len(cafe.reviews) == 1
    assert cafe.reviews[0].submitted_by_id == ANONYMOUS_USER_ID


def test_cafe_external_place_id_is_not_duplicate(db_session, valid_suggestion):
    cafe_external_place_id = valid_suggestion['cafe']['external_place_id']

    check_for_duplicated_cafe(cafe_external_place_id)


def test_cafe_external_place_id_is_duplicated(db_session, valid_suggestion):
    cafe = create_test_cafe(valid_suggestion)

    db_session.add(cafe)
    db_session.commit()

    with pytest.raises(DuplicateCafeError):
        check_for_duplicated_cafe(cafe.external_place_id)
