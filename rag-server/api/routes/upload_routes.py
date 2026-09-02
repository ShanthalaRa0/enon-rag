from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from pathlib import Path
# from uuid import uuid4
import hashlib
import shutil
import logging

from urllib.parse import unquote
from services.database_service import database_service
from services.docdel_service import docdel_service
from orchestration.workflow_manager import start_ingestion_workflow

from config.paths import ORIGINAL_UPLOAD_DIR

router = APIRouter()

logger = logging.getLogger(__name__)

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), overwrite: bool = Form(False),
                           workflow_id: str = Form(...)):

    logger.info(f"overwrite received on server: {overwrite}")
    file.filename = unquote(file.filename)

    existing_document = database_service.get_document_by_filename(
        file.filename
    )
    logger.info(f"existing_document found: {bool(existing_document)}")
    logger.info(f"overwrite flag: {overwrite}")

    if existing_document:
        if not overwrite:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "File already exists",
                    "filename": file.filename,
                    "workflow_id": str(existing_document["workflow_id"]),
                },
            )
        
        # =================================================
        # Delete old document
        # =================================================

        logger.info(
            f"[OVERWRITE] Removing existing document: "
            f"{existing_document['workflow_id']}"
        )
        docdel_service.delete_document(
            workflow_id=str(existing_document["workflow_id"]),
            original_filename=existing_document["original_filename"],
            stored_filename=existing_document["stored_filename"]
        )
    try:

        # workflow_id = str(uuid4())

        logger.info(f"UPLOAD filename received: {file.filename!r}")

        file_extension = Path(file.filename).suffix.lower()

        # stored_file_name = f"{workflow_id}{file_extension}"

        # file_path = ORIGINAL_UPLOAD_DIR / stored_file_name

        original_filename = Path(file.filename).name

        file_path = ORIGINAL_UPLOAD_DIR / original_filename

        stored_file_name = original_filename

        file_saved = False
        database_created = False

        logger.info(f"file_path: {file_path!r}")
        logger.info(f"Original filename: {original_filename!r}")

        # Ensure upload directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving uploaded file to: {file_path}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_saved = True

        await file.seek(0)

        file_bytes = await file.read()

        file_hash = hashlib.md5(file_bytes).hexdigest()

        # Save file information to the database
        database_service.create_document(
            workflow_id=workflow_id,
            original_filename=original_filename,
            stored_filename=stored_file_name,
            file_extension=file_extension,
            mime_type=file.content_type,
            file_size=len(file_bytes),
        )

        database_created = True

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

        if database_created:
            try:
                database_service.delete_document(workflow_id=workflow_id)
            except Exception as delete_error:
                logger.exception(f"Failed to delete database record: {delete_error}"
                    f"{workflow_id}")
        if file_saved:
            try:
                if file_path.exists():
                    file_path.unlink()

                    logger.info(
                        f"[CLEANUP] Deleted original file: "
                        f"{file_path}")

            except Exception:
                logger.exception(
                    f"[CLEANUP] Failed to delete file: "
                    f"{file_path}"
                )        

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )