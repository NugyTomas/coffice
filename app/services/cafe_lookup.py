from sqlalchemy import select

from app.extensions import db
from app.models import Cafe


def mark_existing_cafes(data):
    results = data.get("results", [])
    place_ids = []
    for result in results:
        if result.get("category") == "catering.cafe" and result.get("place_id"):
            place_ids.append(result["place_id"])

    if not place_ids:
        return data

    database_selection = select(Cafe.external_place_id, Cafe.status).where(
        Cafe.external_place_id.in_(place_ids)
    )
    existing_cafes = db.session.execute(database_selection).all()

    status_dict = {place_id: cafe_status.value for place_id, cafe_status in existing_cafes}

    for result in results:
        place_id = result.get("place_id")
        if place_id in status_dict:
            result["coffice_status"] = status_dict[place_id]

    return data
