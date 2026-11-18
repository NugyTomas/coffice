from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

from app.services.photos import save_cafe_photo, delete_photo_files
from tests.helpers import make_photo


def test_save_cafe_photo(tmp_path):
    photo = make_photo()

    photo_path, image_url = save_cafe_photo(photo, ".jpg")

    assert photo_path.exists()
    assert photo_path.parent == tmp_path / "uploads"
    assert image_url.endswith(".jpg")


def test_delete_photo_files(tmp_path):
    photo_path = tmp_path / "photo.jpg"
    photo_path.touch()

    delete_photo_files([photo_path])

    assert not photo_path.exists()


def test_delete_nonexistent_photo_file(tmp_path):
    photo_path = tmp_path / "nonexistent.jpg"

    delete_photo_files([photo_path])

    assert not photo_path.exists()


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
