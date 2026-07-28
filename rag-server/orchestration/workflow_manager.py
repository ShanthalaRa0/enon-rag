import logging

from uuid import uuid4
from datetime import datetime

from orchestration.pipeline_router import route_pipeline

from orchestration.pipeline_status import (
    update_pipeline_status,
)

from orchestration.websocket_events import (
    emit_pipeline_started,
    emit_pipeline_failed,
)

from orchestration.celery_tasks import (
    extract_document_task,
)


logger = logging.getLogger(__name__)


def start_ingestion_workflow(
    file_path: str,
    source_file: str,
    file_hash: str,
    page_number: int,
):

    workflow_id = str(uuid4())

    logger.info(
        f"[WORKFLOW STARTED] workflow_id={workflow_id}"
    )

    try:

        # -----------------------------
        # Select pipeline
        # -----------------------------

        pipeline = route_pipeline(file_path)

        pipeline_name = pipeline.__name__

        logger.info(
            f"[PIPELINE ROUTED] {pipeline_name}"
        )


        # -----------------------------
        # Initial status
        # -----------------------------

        update_pipeline_status(
            workflow_id=workflow_id,
            status="QUEUED",
            stage="INITIALIZED",
            progress=0,
            file_name=source_file,
            created_at=str(datetime.utcnow()),
        )


        # -----------------------------
        # Notify websocket clients
        # -----------------------------

        emit_pipeline_started(
            workflow_id
        )


        # -----------------------------
        # Start celery workflow
        # -----------------------------

        extract_document_task.delay(
            workflow_id=workflow_id,
            file_path=file_path,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
            pipeline_name=pipeline_name,
        )


        logger.info(
            f"[TASK SUBMITTED] workflow_id={workflow_id}"
        )


        return {
            "workflow_id": workflow_id,
            "status": "QUEUED",
            "pipeline": pipeline_name,
        }


    except Exception as e:

        logger.exception(
            "[WORKFLOW FAILED]"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="FAILED",
            stage="WORKFLOW_INITIALIZATION",
            progress=0,
            error=str(e),
        )


        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage="WORKFLOW_INITIALIZATION",
            progress=0,
            error=str(e),
        )

        raise