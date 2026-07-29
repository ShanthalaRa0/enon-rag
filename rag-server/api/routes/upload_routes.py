from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
import hashlib
import shutil
import logging

from services.database_service import database_service
from orchestration.workflow_manager import start_ingestion_workflow

from config.paths import ORIGINAL_UPLOAD_DIR

router = APIRouter()

logger = logging.getLogger(__name__)

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    try:

        workflow_id = str(uuid4())

        file_extension = Path(file.filename).suffix.lower()

        stored_file_name = f"{workflow_id}{file_extension}"

        file_path = ORIGINAL_UPLOAD_DIR / stored_file_name

        # Ensure upload directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving uploaded file to: {file_path}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        await file.seek(0)

        file_bytes = await file.read()

        file_hash = hashlib.md5(file_bytes).hexdigest()

        # Save file information to the database
        database_service.create_document(
            workflow_id=workflow_id,
            original_filename=file.filename,
            stored_filename=stored_file_name,
            file_extension=file_extension,
            mime_type=file.content_type,
            file_size=len(file_bytes),
        )

        workflow = start_ingestion_workflow(
            workflow_id=workflow_id,
            file_path=str(file_path),
            source_file=file.filename,
            file_hash=file_hash,
            page_number=1,
        )

        return {
            "status": "accepted",
            "workflow_id": workflow["workflow_id"],
        }

    except Exception as e:
        logger.exception("Upload failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )