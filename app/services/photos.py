import uuid
from pathlib import Path

from flask import current_app


def save_cafe_photo(photo, extension):
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}{extension}"
    photo_path = upload_folder / unique_filename
    image_url = f"uploads/{unique_filename}"

    try:
        photo.save(photo_path)

    except OSError:
        try:
            photo_path.unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception(
                "Failed to remove incomplete photo: %s",
                photo_path,
            )
        raise

    return photo_path, image_url


def delete_photo_files(paths):
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception("Failed to delete photo file: %s", path)
