from app.enums import (CafeStatus,
                       OpeningDayStatus,
                       WeekDay)
from app.models import (Cafe,
                        CafeFeature,
                        OpeningHours,
                        Review,
                        )


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
