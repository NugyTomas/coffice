import pytest
import json
import copy

from app.enums import CafeStatus
from app.models import Cafe
from sqlalchemy import select, func
from app.routes.suggestions import ANONYMOUS_USER_ID


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


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


@pytest.mark.parametrize("section, field, value", [
    ("cafe", "id", 999),
    ("cafe", "created_at", "2000-01-01"),
    ("cafe", "submitted_by_id", 42),
    ("cafe_features", "id", 999),
    ("cafe_review", "id", 999),
    ("cafe_review", "submitted_by_id", 42),
])
def test_client_cannot_set_system_fields(client, valid_suggestion, db_session, section, field, value):
    data = copy.deepcopy(valid_suggestion)
    data[section][field] = value

    response = client.post('/api/cafe-suggestions',data={"suggestion": json.dumps(data)})
    assert response.status_code == 201


def test_client_cannot_set_submitter_id(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["submitted_by_id"] = 42

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert cafe.submitted_by_id == ANONYMOUS_USER_ID


def test_invalid_opening_hours_intervals(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe_opening_hours"]["monday"]["intervals"] = [
        {"open": "25:70", "close": "20:00"}
    ]

    before_count = db_session.scalar(
        select(func.count()).select_from(Cafe)
    )

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 400

    after_count = db_session.query(Cafe).count()
    assert after_count == before_count
