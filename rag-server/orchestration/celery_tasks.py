# orchestration/celery_tasks.py

import logging

from celery import Celery, chain

from pathlib import Path

from services.extract_file import extract_file

from services.chunking_service import chunk_text

from services.embedding_service import generate_embeddings

from services.vector_store_service import store_embeddings

from orchestration.pipeline_status import (
    update_pipeline_status,
)

from orchestration.websocket_events import (
    emit_pipeline_started,
    emit_pipeline_stage,
    emit_pipeline_completed,
    emit_pipeline_failed,
)

logger = logging.getLogger(__name__)


# =========================================================
# Celery App
# =========================================================

celery_app = Celery(
    "rag_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)
celery_app.conf.task_track_started = True


# =========================================================
# Extraction Task
# =========================================================

@celery_app.task(
    bind=True,
    max_retries=3,
)
def extract_document_task(
    self,
    workflow_id: str,
    file_path: str,
    source_file: str,
    file_hash: str,
    page_number: int,
    pipeline_name: str,
):

    try:

        logger.info(
            f"[EXTRACTION STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="RUNNING",
            stage="TEXT_EXTRACTION",
            progress=20,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage="TEXT_EXTRACTION",
            progress=20,
            message="Extracting document text...",
        )

        # -------------------------------------------------
        # Extract text
        # -------------------------------------------------

        extracted_text = extract_file(
            Path(file_path)
        )

        logger.info(
            f"[EXTRACTION COMPLETED] {workflow_id}"
        )

        # -------------------------------------------------
        # Trigger chunking
        # -------------------------------------------------

        chunk_document_task.delay(
            workflow_id=workflow_id,
            extracted_text=extracted_text,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
        )

    except Exception as e:

        logger.exception(
            "[EXTRACTION FAILED]"
        )

        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage="TEXT_EXTRACTION",
            progress=20,
            error=str(e),
        )

        raise self.retry(
            exc=e,
            countdown=5,
        )


# =========================================================
# Chunking Task
# =========================================================

@celery_app.task(
    bind=True,
    max_retries=3,
)
def chunk_document_task(
    self,
    workflow_id: str,
    extracted_text: str,
    source_file: str,
    file_hash: str,
    page_number: int,
):

    try:

        logger.info(
            f"[CHUNKING STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="RUNNING",
            stage="CHUNKING",
            progress=40,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage="CHUNKING",
            progress=40,
            message="Splitting document into chunks...",
        )

        # -------------------------------------------------
        # Chunk text
        # -------------------------------------------------

        documents = chunk_text(
            extracted_text
        )
        chunks = [
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in documents
        ]

        logger.info(
            f"[CHUNKING COMPLETED] {workflow_id}"
        )

        # -------------------------------------------------
        # Trigger embeddings
        # -------------------------------------------------

        generate_embeddings_task.delay(
            workflow_id=workflow_id,
            chunks=chunks,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
        )

    except Exception as e:

        logger.exception(
            "[CHUNKING FAILED]"
        )

        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage="CHUNKING",
            progress=40,
            error=str(e),
        )

        raise self.retry(
            exc=e,
            countdown=5,
        )


# =========================================================
# Embedding Task
# =========================================================

@celery_app.task(
    bind=True,
    max_retries=3,
)
def generate_embeddings_task(
    self,
    workflow_id: str,
    chunks: list,
    source_file: str,
    file_hash: str,
    page_number: int,
):

    try:

        logger.info(
            f"[EMBEDDING STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="RUNNING",
            stage="EMBEDDING",
            progress=70,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage="EMBEDDING",
            progress=70,
            message="Generating embeddings...",
        )

        # -------------------------------------------------
        # Generate embeddings
        # -------------------------------------------------

        embeddings = generate_embeddings(
            chunks
        )

        logger.info(
            f"[EMBEDDING COMPLETED] {workflow_id}"
        )

        # -------------------------------------------------
        # Store vectors
        # -------------------------------------------------

        store_vectors_task.delay(
            workflow_id=workflow_id,
            embeddings=embeddings,
            chunks=chunks,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
        )

    except Exception as e:

        logger.exception(
            "[EMBEDDING FAILED]"
        )

        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage="EMBEDDING",
            progress=70,
            error=str(e),
        )

        raise self.retry(
            exc=e,
            countdown=5,
        )


# =========================================================
# Vector Store Task
# =========================================================

@celery_app.task(
    bind=True,
    max_retries=3,
)
def store_vectors_task(
    self,
    workflow_id: str,
    embeddings: list,
    chunks: list,
    source_file: str,
    file_hash: str,
    page_number: int,
):

    try:

        logger.info(
            f"[VECTOR STORE STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="RUNNING",
            stage="VECTOR_STORE",
            progress=90,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage="VECTOR_STORE",
            progress=90,
            message="Storing vectors in database...",
        )

        # -------------------------------------------------
        # Store embeddings
        # -------------------------------------------------

        store_embeddings(
            embeddings=embeddings,
            chunks=chunks,
            metadata={
                "source_file": source_file,
                "file_hash": file_hash,
                "page_number": page_number,
            }
        )

        logger.info(
            f"[VECTOR STORE COMPLETED] {workflow_id}"
        )

        # -------------------------------------------------
        # Complete workflow
        # -------------------------------------------------

        complete_workflow_task.delay(
            workflow_id=workflow_id
        )

    except Exception as e:

        logger.exception(
            "[VECTOR STORE FAILED]"
        )

        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage="VECTOR_STORE",
            progress=90,
            error=str(e),
        )

        raise self.retry(
            exc=e,
            countdown=5,
        )


# =========================================================
# Completion Task
# =========================================================

@celery_app.task
def complete_workflow_task(
    workflow_id: str,
):

    logger.info(
        f"[WORKFLOW COMPLETED] {workflow_id}"
    )

    update_pipeline_status(
        workflow_id=workflow_id,
        status="COMPLETED",
        stage="FINISHED",
        progress=100,
    )

    emit_pipeline_completed(
        workflow_id=workflow_id,
    )