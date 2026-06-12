import os
import shutil
import uuid

from fastapi import UploadFile

from app.config import UPLOAD_DIR


def save_upload_file(upload_file: UploadFile) -> tuple[str, str]:
    """Save an uploaded file to UPLOAD_DIR with a UUID-prefixed name.

    Returns (stored_filename, absolute_filepath).
    """
    ext = (upload_file.filename or "").rsplit(".", 1)[-1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.abspath(os.path.join(UPLOAD_DIR, stored_name))
    with open(filepath, "wb") as fh:
        shutil.copyfileobj(upload_file.file, fh)
    return stored_name, filepath


def delete_file(filepath: str) -> None:
    if os.path.exists(filepath):
        os.remove(filepath)
