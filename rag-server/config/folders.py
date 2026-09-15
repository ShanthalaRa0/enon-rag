# config/folders.py

from pathlib import Path

from config.paths import (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR,
)

ROOT_FOLDER = "documents"


def normalize_folder(folder: str | None) -> str:
    if not folder:
        return ROOT_FOLDER

    folder = folder.strip()

    if not folder:
        return ROOT_FOLDER

    if folder == ROOT_FOLDER:
        return ROOT_FOLDER

    # Prevent path traversal
    folder_path = Path(folder)

    if (
        folder_path.is_absolute()
        or ".." in folder_path.parts
    ):
        raise ValueError("Invalid folder name")

    return folder


def ensure_folder(folder: str | None) -> str:
    folder = normalize_folder(folder)

    original_dir = (
        ORIGINAL_UPLOAD_DIR
        if folder == ROOT_FOLDER
        else ORIGINAL_UPLOAD_DIR / folder
    )

    translated_dir = (
        TRANSLATED_UPLOAD_DIR
        if folder == ROOT_FOLDER
        else TRANSLATED_UPLOAD_DIR / folder
    )

    original_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    translated_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return folder