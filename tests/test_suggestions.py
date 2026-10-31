import json

from app.enums import CafeStatus
from app.models import Cafe
from sqlalchemy import select


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_create_cafe_suggestion_success(client, valid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201


def test_create_cafe_suggestion_with_missing_data(client, invalid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(invalid_suggestion)})
    assert response.status_code == 400


def test_create_duplicate_cafe_suggestion(client, valid_suggestion):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 201

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})
    assert response.status_code == 409


def test_status_of_created_cafe_suggestion(client, db_session, valid_suggestion_with_status):
    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion_with_status)})
    stmt = select(Cafe.status).where(Cafe.external_place_id== valid_suggestion_with_status["cafe"]["external_place_id"])
    status_value = db_session.execute(stmt).scalar_one_or_none()

    assert response.status_code == 201
    assert status_value == CafeStatus.PENDING
