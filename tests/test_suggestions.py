import json
import copy

from app.enums import CafeStatus
from app.models import Cafe
from sqlalchemy import select


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


def test_create_duplicate_cafe_suggestion(client, valid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 409


def test_status_of_created_cafe_suggestion(client, db_session, valid_suggestion):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["status"] = "approved"

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})

    stmt = select(Cafe.status).where(Cafe.external_place_id == data["cafe"]["external_place_id"])
    status_value = db_session.execute(stmt).scalar_one_or_none()

    assert response.status_code == 201
    assert status_value == CafeStatus.PENDING
