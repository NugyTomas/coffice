from datetime import datetime
import re

from app.enums import WeekDay, OpeningDayStatus

# =========================================
# CONSTANTS
# =========================================
TIME_TEXT_PATTERN = re.compile(r"\d{2}:\d{2}")
TIME_FORMAT = "%H:%M"


def validate_cafe_opening_hours_data(cafe_opening_hours_data):
    cleaned = {}
    errors = {}

    if not isinstance(cafe_opening_hours_data, dict):
        errors["opening_hours"] = "Cafe opening hours data must be an object."
        return errors, None

    for day in WeekDay:
        day_name = day.value

        if day_name not in cafe_opening_hours_data:
            errors[f"opening_hours_{day_name}"] = f"Opening hours status for {day_name.capitalize()} is required."
            continue

        day_data = cafe_opening_hours_data[day_name]

        if not isinstance(day_data, dict):
            errors[f"opening_hours_{day_name}"] = f"Opening hours data for {day_name.capitalize()} must be an object."
            continue

        cafe_day_status = day_data.get("status")
        if cafe_day_status is None:
            errors[
                f"opening_hours_{day_name}_status"] = f"Opening hours status for {day_name.capitalize()} is required."
            continue

        if not isinstance(cafe_day_status, str):
            errors[
                f"opening_hours_{day_name}_status"] = f"Opening hours status for {day_name.capitalize()} must be a string."
            continue

        try:
            cafe_day_status = OpeningDayStatus(cafe_day_status)
        except ValueError:
            errors[f"opening_hours_{day_name}_status"] = f"Invalid opening hours status for {day_name.capitalize()}."
            continue

        cleaned[day_name] = {}
        cleaned[day_name]["status"] = cafe_day_status

        cafe_day_intervals = day_data.get("intervals")
        if cafe_day_intervals is None:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} are required (use an empty list [] if closed)."
            continue

        if not isinstance(cafe_day_intervals, list):
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be a list."
            continue

        if cafe_day_status is not OpeningDayStatus.OPEN and cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} must be empty when the café is not open."
            continue

        cleaned[day_name]["intervals"] = []

        if cafe_day_status is not OpeningDayStatus.OPEN:
            continue

        if not cafe_day_intervals:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours intervals for {day_name.capitalize()} are required when the café is open."
            continue

        if len(cafe_day_intervals) > 2:
            errors[
                f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} can contain at most two intervals."
            continue

        previous_close_time = None

        for interval in cafe_day_intervals:
            if not isinstance(interval, dict):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours interval for {day_name.capitalize()} must be an object."
                continue

            if set(interval.keys()) != {"open", "close"}:
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours interval for {day_name.capitalize()} must contain only 'open' and 'close'."
                continue

            open_time_text = interval["open"]
            close_time_text = interval["close"]

            if not isinstance(open_time_text, str) or not isinstance(close_time_text, str):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening and closing times for {day_name.capitalize()} must be strings."
                continue

            if not TIME_TEXT_PATTERN.fullmatch(open_time_text) or not TIME_TEXT_PATTERN.fullmatch(close_time_text):
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue

            try:
                open_time = datetime.strptime(open_time_text, TIME_FORMAT).time()
                close_time = datetime.strptime(close_time_text, TIME_FORMAT).time()
            except ValueError:
                errors[
                    f"opening_hours_{day_name}_intervals"] = f"Opening hours for {day_name.capitalize()} must use the HH:MM format."
                continue
            else:
                if previous_close_time is not None and open_time < previous_close_time:
                    errors[
                        f"opening_hours_{day_name}_intervals"] = f"Opening intervals for {day_name.capitalize()} must not overlap."
                    continue

                cleaned[day_name]["intervals"].append({
                    "open": open_time,
                    "close": close_time
                })

                previous_close_time = close_time

    return errors, cleaned
