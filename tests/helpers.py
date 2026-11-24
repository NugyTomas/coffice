from io import BytesIO

from PIL import Image
from werkzeug.datastructures import FileStorage


def make_photo(filename="photo.jpg", fmt="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, fmt)
    buffer.seek(0)

    return FileStorage(stream=buffer, filename=filename)
