import os

from sqlalchemy import select

from app.enums import (CafeStatus,
                       OpeningDayStatus,
                       WeekDay)
from app.extensions import db
from app.models import (Cafe,
                        CafeFeature,
                        CafePhoto,
                        OpeningHours,
                        Review,
                        )
from app.services.photos import save_cafe_photo, delete_photo_files


class DuplicateCafeError(Exception):
    pass


def add_opening_hours(new_cafe, cafe_opening_hours_data):
    for day, data in cafe_opening_hours_data.items():
        day_status = data["status"]
        intervals = (
            data["intervals"]
            if day_status == OpeningDayStatus.OPEN
            else [{}]
        )

        for interval in intervals:
            opening_time = interval.get("open")
            closing_time = interval.get("close")

            cafe_opening_hours = OpeningHours(
                day_of_week=WeekDay(day),
                status=day_status,
                open_time=opening_time,
                close_time=closing_time,
            )

            new_cafe.opening_hours.append(
                cafe_opening_hours
            )


def check_for_duplicated_cafe(external_place_id):
    if not external_place_id:
        return

    database_selection = select(Cafe.external_place_id).where(Cafe.external_place_id == external_place_id)
    existing_cafe = db.session.scalar(database_selection)

    if existing_cafe is not None:
        raise DuplicateCafeError


def build_cafe_suggestion(
        basic_info,
        features,
        opening_hours,
        review,
        submitted_by_id,
):
    new_cafe = Cafe(
        **basic_info,
        submitted_by_id=submitted_by_id,
        status=CafeStatus.PENDING,
    )

    new_cafe.features = CafeFeature(**features)

    add_opening_hours(new_cafe, opening_hours)

    new_cafe.reviews.append(
        Review(**review, submitted_by_id=submitted_by_id)
    )

    return new_cafe


def create_cafe_suggestion(basic_info, features, opening_hours, review, photos, submitted_by_id):
    saved_photo_paths = []
    try:
        check_for_duplicated_cafe(basic_info["external_place_id"])

        new_cafe = build_cafe_suggestion(
            basic_info,
            features,
            opening_hours,
            review,
            submitted_by_id,
        )

        for photo in photos:
            _, extension = os.path.splitext(photo.filename)
            photo_path, image_url = save_cafe_photo(photo, extension)
            saved_photo_paths.append(photo_path)

            new_cafe_photo = CafePhoto(
                image_url=image_url
            )
            new_cafe.photos.append(new_cafe_photo)

        db.session.add(new_cafe)
        db.session.commit()

    except Exception:
        db.session.rollback()
        delete_photo_files(saved_photo_paths)

        raise

    return new_cafe
