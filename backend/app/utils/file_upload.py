import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads/waste_images"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_MB = 5


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_waste_image(file: UploadFile) -> str:
    """
    Saves an uploaded image to disk and returns a relative URL path
    (e.g. "/uploads/waste_images/<uuid>.jpg") to store in image_path.
    """
    ensure_upload_dir()

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large. Max size is {MAX_FILE_SIZE_MB}MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    return f"/{filepath}"
