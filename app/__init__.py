from flask import Flask
from app.extensions import db
from app import models  # noqa: F401  (registers tables for create_all)
from app.config import Config
from app.routes.main import main_bp
from app.routes.geoapify import geoapify_bp
from app.routes.suggestions import suggestions_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(geoapify_bp)
    app.register_blueprint(suggestions_bp)

    with app.app_context():
        db.create_all()
        
    return app
