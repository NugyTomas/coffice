from flask import Flask, render_template

from extensions import db
from models import (Cafe, OpeningHours, CafePhoto, CafeFeature, User, Review,
                    CafeSuggestion, CafeSuggestionOpeningHours, CafeSuggestionPhoto, CafeSuggestionFeature, CafeSuggestionReview)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coffice.db"
db.init_app(app)

with app.app_context():
    db.create_all()

# =========================================
# ROUTES
# =========================================
@app.route('/')
def home():
    return render_template("index.html")

# =========================================
# APPLICATION ENTRY POINT
# =========================================

if __name__ == "__main__":
    app.run(debug=True)