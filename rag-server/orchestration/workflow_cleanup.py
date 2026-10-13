import logging

from services.database_service import database_service
from services.docdel_service import docdel_service

from config.paths import ORIGINAL_UPLOAD_DIR
from pathlib import Path


logger = logging.getLogger(__name__)


def cleanup_failed_workflow(workflow_id: str):
    """
    Cleanup everything belonging to a permanently failed workflow.

    Removes:
    - Document and related records through docdel_service
    - Original uploaded file from the filesystem
    """

    logger.info(
        f"[WORKFLOW CLEANUP STARTED] {workflow_id}"
    )

    try:
        document = database_service.get_document_by_workflow_id(
            workflow_id
        )

        if not document:
            logger.warning(
                f"[WORKFLOW CLEANUP] "
                f"No document found for {workflow_id}"
            )
            return

        folder = document["folder"]
        original_filename = document["original_filename"]
        stored_filename = document["stored_filename"]

        # ---------------------------------------------
        # Determine physical file path
        # ---------------------------------------------

        if folder == "documents":
            file_path = (
                ORIGINAL_UPLOAD_DIR / original_filename
            )
        else:
            file_path = (
                ORIGINAL_UPLOAD_DIR
                / folder
                / original_filename
            )

        logger.info(
            f"[WORKFLOW CLEANUP] File path: {file_path}"
        )

        # ---------------------------------------------
        # Delete document from database/vector store
        # ---------------------------------------------

        docdel_service.delete_document(
            workflow_id=workflow_id,
            folder=folder,
            original_filename=original_filename,
            stored_filename=stored_filename,
        )

        # ---------------------------------------------
        # Delete original physical file
        # ---------------------------------------------

        try:
            if file_path.is_file():
                file_path.unlink()

                logger.info(
                    f"[WORKFLOW CLEANUP] "
                    f"Deleted original file: {file_path}"
                )
            else:
                logger.warning(
                    f"[WORKFLOW CLEANUP] "
                    f"Original file not found: {file_path}"
                )

        except Exception:
            logger.exception(
                f"[WORKFLOW CLEANUP] "
                f"Failed to delete original file: {file_path}"
            )
            raise

        logger.info(
            f"[WORKFLOW CLEANUP COMPLETED] {workflow_id}"
        )

    except Exception:
        logger.exception(
            f"[WORKFLOW CLEANUP FAILED] {workflow_id}"
        )