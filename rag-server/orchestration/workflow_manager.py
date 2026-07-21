# orchestration/workflow_manager.py

import logging
from uuid import uuid4
from pathlib import Path
from datetime import datetime

from orchestration.pipeline_router import route_pipeline

from orchestration.pipeline_status import (
    update_pipeline_status,
)

from orchestration.websocket_events import (
    emit_pipeline_started,
    emit_pipeline_completed,
    emit_pipeline_failed,
    emit_pipeline_stage,
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
    """
    Main orchestration entrypoint.

    Responsibilities:
    - create workflow
    - initialize states
    - choose pipeline
    - trigger async tasks
    - publish events
    """

    workflow_id = str(uuid4())

    logger.info(
        f"[WORKFLOW STARTED] workflow_id={workflow_id}"
    )

    try:

        # -------------------------------------------------
        # Determine pipeline
        # -------------------------------------------------

        pipeline = route_pipeline(file_path)

        pipeline_name = pipeline.__name__

        logger.info(
            f"[PIPELINE ROUTED] {pipeline_name}"
        )

        # -------------------------------------------------
        # Initial workflow state
        # -------------------------------------------------

        update_pipeline_status(
            workflow_id=workflow_id,
            status="QUEUED",
            stage="INITIALIZED",
            progress=0,
            file_name=source_file,
            created_at=str(datetime.utcnow()),
        )

        # -------------------------------------------------
        # Emit started event
        # -------------------------------------------------

        emit_pipeline_started(
            workflow_id=workflow_id,
            data={
                "pipeline": pipeline_name,
                "file": source_file,
            }
        )

        # -------------------------------------------------
        # Update extraction stage
        # -------------------------------------------------

        update_pipeline_status(
            workflow_id=workflow_id,
            status="RUNNING",
            stage="TEXT_EXTRACTION",
            progress=10,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage="TEXT_EXTRACTION",
            progress=10,
        )

        # -------------------------------------------------
        # Trigger async extraction task
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Return immediately
        # -------------------------------------------------

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
            error=str(e),
        )

        raise