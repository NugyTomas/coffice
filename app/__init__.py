from flask import Flask
from app.extensions import db
from app import models
from app.config import Config
from app.routes.main import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        
    return app
