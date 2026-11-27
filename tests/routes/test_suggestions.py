import copy
import json
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.constants import ANONYMOUS_USER_ID
from app.enums import CafeStatus
from app.models import Cafe
from app.services import suggestions
from app.routes.suggestions import DUPLICATE_CAFE_ERROR
from tests.helpers import make_photo


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.parametrize("expected_element", [
    'name="cafeName"',
    'name="cafeAddress"',
    'name="cafeCity"',
    'name="cafePostCode"',
    'name="cafePhone"',
    'name="cafeEmail"',
    'name="cafeWebsite"',
    'name="cafeInstagram"',
    'name="userReview"',

    'name="cafePrice"',
    'name="coffeeQuality"',

    'data-day="monday"',
    'data-day="tuesday"',
    'data-day="wednesday"',
    'data-day="thursday"',
    'data-day="friday"',
    'data-day="saturday"',
    'data-day="sunday"',

    'id="cafe-photo-input"',
])
def test_suggest_cafe_page_contains_form_fields(client, expected_element):
    response = client.get("/suggest-cafe")

    assert response.status_code == 200
    html = response.text

    assert expected_element in html


def test_create_cafe_suggestion_success(client, valid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201


def test_missing_longitude_returns_400(client, valid_suggestion):
    data = copy.deepcopy(valid_suggestion)
    del data["cafe"]["longitude"]

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 400
    assert "longitude" in response.get_json()["errors"]


def test_duplicated_cafe_suggestion_returns_409(client, valid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 409


def test_status_of_created_cafe_suggestion(client, db_session, valid_suggestion):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["status"] = "approved"

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert cafe.status == CafeStatus.PENDING


def test_invalid_opening_hours_intervals(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe_opening_hours"]["monday"]["intervals"] = [
        {"open": "25:70", "close": "20:00"}
    ]

    before_count = db_session.scalar(select(func.count()).select_from(Cafe))

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 400

    after_count = db_session.scalar(select(func.count()).select_from(Cafe))
    assert after_count == before_count


@pytest.mark.parametrize("section", [
    "cafe",
    "cafe_features",
    "cafe_review"])
def test_client_cannot_set_id(client, valid_suggestion, db_session, section):
    data = copy.deepcopy(valid_suggestion)
    data[section]["id"] = 999

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    if section == "cafe":
        assert cafe.id != 999
    elif section == "cafe_features":
        assert cafe.features.id != 999
    elif section == "cafe_review":
        assert cafe.reviews[0].id != 999


@pytest.mark.parametrize("section", [
    "cafe",
    "cafe_review"])
def test_client_cannot_set_submitter_id(client, valid_suggestion, db_session, section):
    data = copy.deepcopy(valid_suggestion)
    data[section]["submitted_by_id"] = 42

    response = client.post("/api/cafe-suggestions", data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    if section == "cafe":
        assert cafe.submitted_by_id == ANONYMOUS_USER_ID
    elif section == "cafe_review":
        assert cafe.reviews[0].submitted_by_id == ANONYMOUS_USER_ID


def test_client_cannot_set_created_at(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["created_at"] = "2000-01-01"

    request_time = datetime.now()

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert request_time <= cafe.created_at <= datetime.now()


def test_cafe_suggestion_without_external_place_id_returns_201(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    del data["cafe"]["external_place_id"]

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert cafe.external_place_id is None


def test_integrity_error_returns_409_and_cleans_uploads(app, client, monkeypatch, valid_suggestion, db_session):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201

    real_check = suggestions.check_for_duplicated_cafe
    calls = []

    def skip_first_check(external_place_id):
        calls.append(external_place_id)
        if len(calls) == 1:
            return
        real_check(external_place_id)

    monkeypatch.setattr(
        suggestions,
        "check_for_duplicated_cafe",
        skip_first_check,
    )

    def mock_commit():
        raise IntegrityError(
            "INSERT INTO cafes ...",
            {},
            Exception("Simulated unique constraint violation"),
        )

    monkeypatch.setattr(
        db_session,
        "commit",
        mock_commit
    )

    response = client.post("/api/cafe-suggestions",
                           data={"suggestion": json.dumps(valid_suggestion), "photos": make_photo("test.jpg")})
    upload_folder = Path(app.config["UPLOAD_FOLDER"])

    assert response.status_code == 409
    assert response.get_json()["success"] is False
    assert response.get_json()["errors"]["cafe"] == DUPLICATE_CAFE_ERROR
    assert len(calls) == 2
    assert list(upload_folder.iterdir()) == []

    cafe_count = db_session.scalar(
        select(func.count()).select_from(Cafe)
    )
    assert cafe_count == 1
