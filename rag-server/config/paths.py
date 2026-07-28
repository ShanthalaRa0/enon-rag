from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
ORIGINAL_UPLOAD_DIR = UPLOAD_DIR / "originals"
TRANSLATED_UPLOAD_DIR = UPLOAD_DIR / "translated"

VECTOR_STORE_DIR = BASE_DIR / "vector_store"
TEMP_DIR = BASE_DIR / "temp"
LOG_DIR = BASE_DIR / "logs"

for directory in (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR,
    VECTOR_STORE_DIR,
    TEMP_DIR,
    LOG_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)