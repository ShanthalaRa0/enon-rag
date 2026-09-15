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


@router.get("/workspace/file/{file_path:path}")
async def workspace_file(file_path: str):

    file_path = file_path.strip("/")

    logger.info(
        f"Requested workspace path: {file_path}"
    )

    supported_types = {
        "txt": {
            "directory": TRANSLATED_UPLOAD_DIR,
            "media_type": "text/plain",
        },

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

    # ---------------------------------------------
    # Get extension
    # ---------------------------------------------

    extension = (
        file_path.rsplit(".", 1)[-1]
        .lower()
        .strip()
    )

    if extension not in supported_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    # ---------------------------------------------
    # Determine storage directory
    # ---------------------------------------------

    if file_path.startswith("originals/"):

        relative_path = file_path[
            len("originals/"):
        ]

        base_directory = (
            ORIGINAL_UPLOAD_DIR.resolve()
        )

    elif file_path.startswith("translated/"):

        relative_path = file_path[
            len("translated/"):
        ]

        base_directory = (
            TRANSLATED_UPLOAD_DIR.resolve()
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid workspace path",
        )

    # ---------------------------------------------
    # Build actual filesystem path
    # ---------------------------------------------

    actual_path = (
        base_directory / relative_path
    ).resolve()

    logger.info(
        f"Resolved workspace path: {actual_path}"
    )

    # ---------------------------------------------
    # Security check
    # ---------------------------------------------

    if not actual_path.is_relative_to(
        base_directory
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path",
        )

    # ---------------------------------------------
    # File existence
    # ---------------------------------------------

    if not actual_path.exists():
        logger.warning(
            f"Workspace file not found: {actual_path}"
        )

        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if not actual_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Not a file",
        )

    # ---------------------------------------------
    # Return file
    # ---------------------------------------------

    return FileResponse(
        path=actual_path,
        media_type=supported_types[
            extension
        ]["media_type"],
        filename=actual_path.name,
    )