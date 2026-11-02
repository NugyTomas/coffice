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

def test_client_cannot_set_system_managed_cafe_fields(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["id"] = 999
    data["cafe"]["created_at"] = "2000-01-01"

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})

    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert cafe.id != 999

def test_client_cannot_set_submitter_id(client, valid_suggestion, db_session):
    data = copy.deepcopy(valid_suggestion)
    data["cafe"]["submitted_by_id"] = 42

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(data)})
    assert response.status_code == 201

    cafe = db_session.scalars(select(Cafe)).one()
    assert cafe.submitted_by_id != 42