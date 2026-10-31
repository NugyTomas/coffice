import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_suggestion():
    return {"cafe": {"external_place_id": "test-place-001",
                     "name": "Test Cafe",
                     "address": "Testovaci 123",
                     "city": "Pilsen",
                     "postal_code": "301 00",
                     "latitude": 49.7280338,
                     "longitude": 13.3676314,
                     "website": "test.com",
                     "price_level": "medium",
                     "coffee_quality": "medium"},

            "cafe_features": {"wifi_quality": "unavailable",
                              "power_outlets": "everywhere",
                              "noise_level": "quiet",
                              "seating_type": "unknown",
                              "air_conditioning": "unknown",
                              "typical_occupancy": "low",
                              "card_payment": "yes",
                              "food_options": "unavailable",
                              "vegetarian_options": "unavailable"},

            "cafe_opening_hours": {"sunday": {"status": "closed", "intervals": []},
                                   "monday": {"status": "open", "intervals": [{"open": "07:00", "close": "20:00"}]},
                                   "tuesday": {"status": "open", "intervals": [{"open": "07:00", "close": "20:00"}]},
                                   "wednesday": {"status": "open", "intervals": [{"open": "07:00", "close": "20:00"}]},
                                   "thursday": {"status": "open", "intervals": [{"open": "07:00", "close": "20:00"}]},
                                   "friday": {"status": "open", "intervals": [{"open": "07:00", "close": "20:00"}]},
                                   "saturday": {"status": "open", "intervals": [{"open": "08:00", "close": "19:00"}]}},

            "cafe_review": {"rating": "5",
                            "text": "Super!"}
            }


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
