from flask import Blueprint, render_template

from app.enums import WeekDay

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/suggest-cafe")
def suggest_cafe():
    return render_template("suggest-cafe.html", weekdays=[d.value for d in WeekDay])
