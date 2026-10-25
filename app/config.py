import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///coffice.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CHECK_EMAIL_DELIVERABILITY = True
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    CHECK_EMAIL_DELIVERABILITY = False