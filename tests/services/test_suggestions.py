import copy
import json
from pathlib import Path

import pytest
from flask import current_app
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from app.constants import ANONYMOUS_USER_ID
from app.enums import CafeStatus
from app.models import (Cafe,
                        CafeFeature,
                        CafePhoto,
                        OpeningHours,
                        Review,
                        )
from app.services.suggestions import (create_cafe_suggestion,
                                      check_for_duplicated_cafe,
                                      DuplicateCafeError,
                                      )
from app.validators.suggestions import validate_suggestion_data
from tests.helpers import make_photo


def create_and_save_test_cafe(valid_suggestion):
    suggestion_json = json.dumps(valid_suggestion)
    photo = [make_photo("test.jpg")]

    (
        errors,
        basic_info,
        features,
        opening_hours,
        review,
        photos,
    ) = validate_suggestion_data(suggestion_json, photo)

    assert errors == {}

    return create_cafe_suggestion(
        basic_info,
        features,
        opening_hours,
        review,
        photos,
        ANONYMOUS_USER_ID,
    )


def test_create_cafe_suggestion_success(db_session, valid_suggestion):
    cafe = create_and_save_test_cafe(valid_suggestion)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    db_count = db_session.scalar(select(func.count()).select_from(CafePhoto))

    assert cafe.status == CafeStatus.PENDING
    assert cafe.submitted_by_id == ANONYMOUS_USER_ID
    assert len(cafe.opening_hours) == 7
    assert cafe.features is not None
    assert len(cafe.reviews) == 1
    assert cafe.reviews[0].submitted_by_id == ANONYMOUS_USER_ID
    assert upload_folder.exists()
    assert len(list(upload_folder.iterdir())) == 1
    assert db_count == 1
    assert len(cafe.photos) == 1


def test_cafe_external_place_id_is_not_duplicate(valid_suggestion):
    cafe_external_place_id = valid_suggestion['cafe']['external_place_id']

    check_for_duplicated_cafe(cafe_external_place_id)


@pytest.mark.parametrize("external_place_id", [None, ""])
def test_empty_external_place_id_is_not_checked(db_session, monkeypatch, external_place_id):
    def mock_scalar(*args, **kwargs):
        pytest.fail("Database query should not be executed.")

    monkeypatch.setattr(
        db_session,
        "scalar",
        mock_scalar
    )

    check_for_duplicated_cafe(external_place_id)


def test_cafe_without_external_place_id(db_session, valid_suggestion):
    data = copy.deepcopy(valid_suggestion)
    del data["cafe"]["external_place_id"]

    for loop in range(3):
        create_and_save_test_cafe(data)

    db_count = db_session.scalar(select(func.count()).select_from(Cafe))
    assert db_count == 3


def test_cafe_external_place_id_is_duplicated(db_session, valid_suggestion):
    create_and_save_test_cafe(valid_suggestion)

    with pytest.raises(DuplicateCafeError):
        create_and_save_test_cafe(valid_suggestion)

    db_count = db_session.scalar(select(func.count()).select_from(Cafe))
    assert db_count == 1


def test_error_while_committing_to_db(db_session, monkeypatch, valid_suggestion):
    def mock_commit():
        raise SQLAlchemyError("Simulated commit failure")

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])

    monkeypatch.setattr(
        db_session,
        "commit",
        mock_commit
    )

    with pytest.raises(SQLAlchemyError):
        create_and_save_test_cafe(valid_suggestion)
    assert len(list(upload_folder.iterdir())) == 0

    basic_info_db_count = db_session.scalar(select(func.count()).select_from(Cafe))
    features_db_count = db_session.scalar(select(func.count()).select_from(CafeFeature))
    opening_hours_db_count = db_session.scalar(select(func.count()).select_from(OpeningHours))
    review_db_count = db_session.scalar(select(func.count()).select_from(Review))
    photos_db_count = db_session.scalar(select(func.count()).select_from(CafePhoto))

    assert basic_info_db_count == 0
    assert features_db_count == 0
    assert opening_hours_db_count == 0
    assert review_db_count == 0
    assert photos_db_count == 0
