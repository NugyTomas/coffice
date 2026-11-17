import os

from PIL import Image, UnidentifiedImageError

# =========================================
# CONSTANTS
# =========================================
MAX_ALLOWED_PHOTOS = 6
ALLOWED_PHOTO_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
PHOTO_FORMATS_BY_EXTENSION = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}
MAX_ALLOWED_PHOTO_SIZE = 5 * 1024 * 1024

PHOTO_LIST_ERROR = "Cafe photos must be a list."
PHOTO_COUNT_ERROR = "Cafe photos must contain at most 6 photos."
PHOTO_TYPE_ERROR = "Only JPG, PNG and WebP photo types are allowed."
PHOTO_EXTENSION_MISMATCH_ERROR = "The image content does not match its file extension."
INVALID_PHOTO_ERROR = "The uploaded file is not a valid image."
PHOTO_SIZE_ERROR = "Maximum size of a photo is 5 MB."


# =================== MAIN FUNCTION ======================
def validate_cafe_photos(cafe_photos):
    errors = {}

    if not isinstance(cafe_photos, list):
        errors["cafe_photos"] = PHOTO_LIST_ERROR
        return errors

    if len(cafe_photos) > MAX_ALLOWED_PHOTOS:
        errors["cafe_photos"] = PHOTO_COUNT_ERROR
        return errors

    for photo in cafe_photos:
        filename = photo.filename
        _, extension = os.path.splitext(filename)
        extension = extension.lower()

        error_key = f"cafe_photos_{filename}"

        if extension not in ALLOWED_PHOTO_TYPES:
            errors.setdefault(error_key, []).append(PHOTO_TYPE_ERROR)

        else:
            try:
                with Image.open(photo) as image:
                    actual_format = image.format
                    image.verify()

                expected_format = PHOTO_FORMATS_BY_EXTENSION[extension]

                if actual_format != expected_format:
                    errors.setdefault(error_key, []).append(PHOTO_EXTENSION_MISMATCH_ERROR)

            except (UnidentifiedImageError,
                    OSError,
                    Image.DecompressionBombError,
                    SyntaxError,
                    ValueError,):
                errors.setdefault(error_key, []).append(INVALID_PHOTO_ERROR)

            finally:
                photo.seek(0)

        photo.seek(0, os.SEEK_END)
        photo_size = photo.tell()
        photo.seek(0)

        if photo_size > MAX_ALLOWED_PHOTO_SIZE:
            errors.setdefault(error_key, []).append(PHOTO_SIZE_ERROR)

    return errors
