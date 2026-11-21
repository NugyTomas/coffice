from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

from app.services.photos import save_cafe_photo, delete_photo_files
from tests.helpers import make_photo


def test_save_cafe_photo(app):
    photo = make_photo()
    upload_folder = Path(app.config["UPLOAD_FOLDER"])

    with app.app_context():
        photo_path, image_url = save_cafe_photo(photo, ".jpg")

    assert photo_path.exists()
    assert photo_path.parent == upload_folder
    assert image_url.endswith(".jpg")


def test_delete_photo_files(app):
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    photo_path = upload_folder / "photo.jpg"
    photo_path.touch()

    with app.app_context():
        delete_photo_files([photo_path])

    assert not photo_path.exists()


def test_delete_nonexistent_photo_file(app):
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    photo_path = upload_folder / "nonexistent.jpg"

    with app.app_context():
        delete_photo_files([photo_path])

    assert not photo_path.exists()


def test_delete_photo_file_handles_os_error(app, monkeypatch, caplog):
    photo_path = Path(app.config["UPLOAD_FOLDER"]) / "photo.jpg"

    def fail_unlink(self, missing_ok=False):
        raise OSError("simulated delete failure")

    monkeypatch.setattr(Path, "unlink", fail_unlink)

    with app.app_context():
        delete_photo_files([photo_path])
        assert "Failed to delete photo file" in caplog.text


def test_save_cafe_photo_cleans_partial_file_on_error(app, monkeypatch):
    photo = make_photo()

    def fail_save(self, dst, *args, **kwargs):
        Path(dst).write_bytes(b"partial file")
        raise OSError("simulated save failure")

    monkeypatch.setattr(FileStorage, "save", fail_save)

    with app.app_context():
        with pytest.raises(OSError, match="simulated save failure"):
            save_cafe_photo(photo, ".jpg")

    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    assert list(upload_folder.iterdir()) == []
