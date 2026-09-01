import logging

from services.database_service import database_service
from services.docdel_service import docdel_service

logger = logging.getLogger(__name__)


def cleanup_failed_workflow(workflow_id: str):
    """
    Cleanup everything belonging to a failed workflow.

    This should only be called when the workflow has
    permanently failed after all Celery retries.
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

        # -------------------------------------------------
        # Delete document/files
        # -------------------------------------------------

        docdel_service.delete_document(
            workflow_id=workflow_id,
            original_filename=document["original_filename"],
            stored_filename=document["stored_filename"],
        )

        logger.info(
            f"[WORKFLOW CLEANUP COMPLETED] {workflow_id}"
        )

    except Exception:

        logger.exception(
            f"[WORKFLOW CLEANUP FAILED] {workflow_id}"
        )