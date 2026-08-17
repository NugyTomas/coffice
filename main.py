from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Text, Float


app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafes(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geoapify_place_id : Mapped[str] = mapped_column(String(250), unique= True, nullable=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(250), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str] = mapped_column(String(250), nullable=True)
    email : Mapped[str] = mapped_column(String(250), nullable=True)
    website : Mapped[str] = mapped_column(String(250), nullable=True)
    instagram : Mapped[str] = mapped_column(String(250), nullable=True)
    price_level: Mapped[str] = mapped_column(String(250), nullable=True)


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