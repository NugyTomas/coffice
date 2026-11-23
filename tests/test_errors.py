import json

from flask import request

from app.routes import suggestions
from app.errors import SOMETHING_WENT_WRONG_ERROR, REQUEST_TOO_LARGE_ERROR


def test_get_nonexistent_url_returns_404_for_api(app, client):
    response = client.get('/api/nonexistent')

    assert response.status_code == 404
    assert response.mimetype == "application/json"
    assert response.get_json()["success"] is False
    assert response.get_json()["errors"]["request"]


def test_get_nonexistent_url_returns_404_for_web(client):
    response = client.get('/kafe')

    assert response.status_code == 404
    assert response.mimetype == "text/html"


def test_unexpected_python_exception_returns_500_for_api(client, monkeypatch, valid_suggestion):
    def raise_value_error(*args, **kwargs):
        raise ValueError("Test error")

    monkeypatch.setattr(suggestions, "create_cafe_suggestion", raise_value_error)

    response = client.post('/api/cafe-suggestions', data={"suggestion": json.dumps(valid_suggestion)})

    assert response.status_code == 500
    assert response.mimetype == "application/json"
    assert response.get_json()["success"] is False
    assert response.get_json()["errors"]["server"] == SOMETHING_WENT_WRONG_ERROR
    assert "Test error" not in response.get_data(as_text=True)


def test_get_cafe_suggestions_returns_405_for_api(client):
    response = client.get('/api/cafe-suggestions')

    assert response.status_code == 405
    assert response.mimetype == "application/json"
    assert response.get_json()["success"] is False
    assert response.get_json()["errors"]["request"]


def test_request_too_large_returns_413_for_api(app, client):
    app.config["MAX_CONTENT_LENGTH"] = 100

    response = client.post('/api/cafe-suggestions', data="x" * 101, content_type="application/x-www-form-urlencoded")

    assert response.status_code == 413
    assert response.mimetype == "application/json"
    assert response.get_json()["success"] is False
    assert response.get_json()["errors"]["request"] == REQUEST_TOO_LARGE_ERROR


def test_request_too_large_returns_413_for_web(app, client):
    app.config["MAX_CONTENT_LENGTH"] = 100

    def request_data():
        request.get_data()

    app.add_url_rule("/test/route", view_func=request_data, methods=['POST'])

    response = client.post("/test/route", data="x" * 101, content_type="text/html")

    assert response.status_code == 413
    assert response.mimetype == "text/html"
    assert response.is_json is False


def test_unexpected_python_exception_returns_500_for_web(app, client):
    def raise_value_error(*args, **kwargs):
        raise ValueError("Test error")

    app.add_url_rule("/test/route", view_func=raise_value_error)

    response = client.get('/test/route')

    assert response.status_code == 500
    assert response.mimetype == "text/html"
    assert response.is_json is False
    assert "Test error" not in response.get_data(as_text=True)
