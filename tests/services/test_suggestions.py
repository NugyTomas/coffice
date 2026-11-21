import json

from app.constants import ANONYMOUS_USER_ID
from app.enums import CafeStatus
from app.services.suggestions import build_cafe_suggestion
from app.validators.suggestions import validate_suggestion_data


def test_build_cafe_suggestion(valid_suggestion):
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

    cafe = build_cafe_suggestion(
        basic_info,
        features,
        opening_hours,
        review,
        ANONYMOUS_USER_ID,
    )

    assert cafe.status == CafeStatus.PENDING
    assert cafe.submitted_by_id == ANONYMOUS_USER_ID
    assert len(cafe.opening_hours) == 7
    assert cafe.features is not None
    assert len(cafe.reviews) == 1
    assert cafe.reviews[0].submitted_by_id == ANONYMOUS_USER_ID