from io import BytesIO

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.validators.suggestions import validate_cafe_photos


def make_photo(filename="photo.jpg", fmt="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, fmt)
    buffer.seek(0)
    return FileStorage(stream=buffer, filename=filename)


@pytest.mark.parametrize("raw", [
    None,
    "photo.jpg",
    123,
    {},
    ()
])
def test_invalid_photos_data_type(raw):
    errors = validate_cafe_photos(raw)

    assert "cafe_photos" in errors


def test_empty_photo_list_is_valid():
    errors = validate_cafe_photos([])

    assert errors == {}


def test_valid_number_of_photos():
    photos = [make_photo() for _ in range(6)]

    errors = validate_cafe_photos(photos)

    assert "cafe_photos" not in errors
    assert errors == {}


def test_invalid_number_of_photos():
    photos = [make_photo() for _ in range(7)]

    errors = validate_cafe_photos(photos)

    assert "cafe_photos" in errors


@pytest.mark.parametrize("filename, fmt", [
    ("photo.jpg", "JPEG"),
    ("photo.jpeg", "JPEG"),
    ("photo.png", "PNG"),
    ("photo.webp", "WEBP"),
    ("PHOTO.JPG", "JPEG")
])
def test_valid_photo_formats(filename, fmt):
    photo = [make_photo(filename, fmt)]

    errors = validate_cafe_photos(photo)

    assert f"cafe_photos_{filename}" not in errors
    assert errors == {}


@pytest.mark.parametrize("filename, fmt", [
    ("photo.gif", "GIF"),
    ("photo.bmp", "BMP"),
    ("photo.tiff", "TIFF"),
    ("photo", "JPEG")
])
def test_invalid_photo_format(filename, fmt):
    photo = [make_photo(filename, fmt)]

    errors = validate_cafe_photos(photo)

    assert errors[f"cafe_photos_{filename}"] == ["Only JPG, PNG and WebP photo types are allowed."]


@pytest.mark.parametrize("filename, fmt", [
    ("photo.jpg", "PNG"),
    ("photo.jpeg", "WEBP"),
    ("photo.png", "JPEG"),
    ("photo.webp", "PNG")
])
def test_photo_format_does_not_match_name(filename, fmt):
    photo = [make_photo(filename, fmt)]

    errors = validate_cafe_photos(photo)

    assert errors[f"cafe_photos_{filename}"] == ["The image content does not match its file extension."]


def test_photo_too_large(monkeypatch):
    monkeypatch.setattr(
        "app.validators.suggestions.MAX_ALLOWED_PHOTO_SIZE",
        100
    )

    photo = make_photo()

    photo.seek(0, 2)
    photo_size = photo.tell()
    photo.seek(0)

    assert photo_size > 100

    errors = validate_cafe_photos([photo])

    assert errors["cafe_photos_photo.jpg"] == [
        "Maximum size of a photo is 5 MB."
    ]


def test_corrupted_photo():
    photo = FileStorage(
        stream=BytesIO(b"This is not a valid image."),
        filename="photo.jpg"
    )

    errors = validate_cafe_photos([photo])

    assert errors["cafe_photos_photo.jpg"] == [
        "The uploaded file is not a valid image."
    ]


def test_empty_photo_file():
    photo = FileStorage(
        stream=BytesIO(b""),
        filename="photo.jpg"
    )

    errors = validate_cafe_photos([photo])

    assert errors["cafe_photos_photo.jpg"] == [
        "The uploaded file is not a valid image."
    ]
