from sqlalchemy import select

from app.extensions import db
from app.models import Cafe, CafeSuggestion


def mark_existing_cafes(data):
    results = data.get("results", [])
    place_ids = []
    for result in results:
        if result.get("category") == "catering.cafe" and result.get("place_id"):
            place_ids.append(result["place_id"])

    if not place_ids:
        return data

    approved = set(
        db.session.scalars(
            select(Cafe.external_place_id).where(
                Cafe.external_place_id.in_(place_ids)
            )
        )
    )

    pending = set(
        db.session.scalars(
            select(CafeSuggestion.external_place_id).where(
                CafeSuggestion.external_place_id.in_(place_ids)
            )
        )
    )

    for result in results:
        if result.get("place_id") in approved:
            result["coffice_status"] = "approved"
        elif result.get("place_id") in pending:
            result["coffice_status"] = "pending"

    return data
