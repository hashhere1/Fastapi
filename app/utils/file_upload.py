import uuid
import os
import shutil
from fastapi import HTTPException, UploadFile

UPLOAD_DIR = "app/uploads/profile_pictures"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


def upload_image(profile_pic: UploadFile) -> str:
    if profile_pic.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, WEBP and GIF images are allowed"
        )
    upload_directory = "app/uploads/profile_pictures"
    os.makedirs(upload_directory, exist_ok=True)

    filename = f"{uuid.uuid4()}_{profile_pic.filename}"
    file_path = os.path.join(upload_directory, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_pic.file, buffer)

    return f"profile_pictures/{filename}"