from pathlib import Path
import logging
from services.database_service import database_service
from services.vector_store_service import delete_by_workflow_id

from config.paths import (
    ORIGINAL_UPLOAD_DIR,
    TRANSLATED_UPLOAD_DIR,
)
logger = logging.getLogger(__name__)


class DocdelService:

    def __init__(
        self,
        database_service,
        original_upload_dir,
        translated_upload_dir,
    ):
        self.database_service = database_service
        self.original_upload_dir = original_upload_dir
        self.translated_upload_dir = translated_upload_dir

    def delete_document(
        self,
        workflow_id: str,
        stored_filename: str,
    ):
        # 1. Delete vectors
        try:
            delete_by_workflow_id(workflow_id)

            logger.info(
                f"[VECTORS DELETED] {workflow_id}"
            )
        except Exception:
            logger.exception(
                f"[VECTOR DELETE FAILED] {workflow_id}"
            )
            raise

        # 2. Delete original file
        original_file = (
            self.original_upload_dir / stored_filename
        )

        if original_file.exists():
            original_file.unlink()

            logger.info(
                f"[ORIGINAL FILE DELETED] {original_file}"
            )

        # 3. Delete translated file
        translated_file = (
            self.translated_upload_dir
            / f"{workflow_id}.txt"
        )

        logger.info(f"[CHECK TRANSLATED FILE] {translated_file}")

        logger.info(
            f"[EXISTS] {translated_file.exists()}"
        )

        if translated_file.exists():
            translated_file.unlink()

            logger.info(
                f"[TRANSLATED FILE DELETED] {translated_file}"
            )

        # 4. Delete database record
        self.database_service.delete_document(
            workflow_id
        )

        logger.info(
            f"[DOCUMENT DELETED] {workflow_id}"
        )

docdel_service = DocdelService(
    database_service=database_service,
    original_upload_dir=ORIGINAL_UPLOAD_DIR,
    translated_upload_dir=TRANSLATED_UPLOAD_DIR,
)
        