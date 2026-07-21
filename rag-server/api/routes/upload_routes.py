from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
import hashlib
import shutil
import logging

from orchestration.workflow_manager import start_ingestion_workflow
from orchestration.pipeline_router import route_pipeline

router = APIRouter()

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    try:

        job_id = str(uuid4())

        file_extension = Path(file.filename).suffix.lower()

        stored_file_name = f"{job_id}{file_extension}"

        file_path = UPLOAD_DIR / stored_file_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        await file.seek(0)

        file_bytes = await file.read()

        file_hash = hashlib.md5(file_bytes).hexdigest()

        workflow = start_ingestion_workflow(
            file_path=str(file_path),
            source_file=file.filename,
            file_hash=file_hash,
            page_number=1,
        )

        return {
            "status": "accepted",
            "job_id": job_id,
            "workflow_id": workflow["workflow_id"],
            "pipeline": workflow["pipeline"],
        }

    except Exception as e:
        logger.exception("Upload failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )