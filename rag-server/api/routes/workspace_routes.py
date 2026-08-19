from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import logging

from config.paths import (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR,
)
from services.workspace_service import get_workspace

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/workspace")
async def workspace_route():

    try:

        result = get_workspace()

        return {
            "message": "success",
            "results": result
        }

    except Exception as e:

        logger.exception("Workspace loading failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/workspace/file/{filename}")
async def workspace_file(filename: str):

    extension = filename.rsplit(".", 1)[-1].lower().strip()

    logger.info(
        f"Requested file: {filename}, extension: {extension}"
    )

    supported_types = {
        # Translated files
        "txt": {
            "directory": TRANSLATED_UPLOAD_DIR,
            "media_type": "text/plain",
        },

        # Original documents
        "pdf": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "application/pdf",
        },
        "doc": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "application/msword",
        },
        "docx": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": (
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
        },
        "xls": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "application/vnd.ms-excel",
        },
        "xlsx": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": (
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
        },
        "ppt": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "application/vnd.ms-powerpoint",
        },
        "pptx": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": (
                "application/vnd.openxmlformats-"
                "officedocument.presentationml.presentation"
            ),
        },

        # Images
        "jpg": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "image/jpeg",
        },
        "jpeg": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "image/jpeg",
        },
        "png": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "image/png",
        },
        "gif": {
            "directory": ORIGINAL_UPLOAD_DIR,
            "media_type": "image/gif",
        },
    }

    if extension not in supported_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    base_directory = supported_types[extension]["directory"].resolve()

    file_path = (base_directory / filename).resolve()

    if base_directory not in file_path.parents:
        raise HTTPException(
            status_code=400,
            detail="Invalid file path",
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Not a file",
        )

    return FileResponse(
        path=file_path,
        media_type=supported_types[extension]["media_type"],
        filename=file_path.name,
    )