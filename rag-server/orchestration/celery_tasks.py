# orchestration/celery_tasks.py

import logging

from celery import Celery, chain

from pathlib import Path

from services.extract_file import extract_file

from services.translation_service import translation_service

from services.chunking_service import chunk_text

from services.embedding_service import generate_embeddings

from services.vector_store_service import store_embeddings

from workflow.event_types import WorkflowStage

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
):

    try:

        logger.info(
            f"[EXTRACTION STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="EXTRACTING",
            stage=WorkflowStage.EXTRACTING,
            progress=40,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage=WorkflowStage.EXTRACTING,
            progress=40,
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
        # Translate text
        # -------------------------------------------------
        translate_document_task.delay(
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
            stage=WorkflowStage.EXTRACTING,
            progress=40,
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
    original_text: str,
    translated_text: str | None,
    original_language: str,
    translated_language: str | None,
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
            status="CHUNKING",
            stage=WorkflowStage.CHUNKING,
            progress=50,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage=WorkflowStage.CHUNKING,
            progress=50,
            message="Splitting original and translated text into chunks...",
        )

        # -------------------------------------------------
        # Original chunks
        # -------------------------------------------------

        original_documents = chunk_text(
            text=original_text,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
            workflow_id=workflow_id,
            file_type="original",
            language=original_language,
        )

        original_chunks = []

        for doc in original_documents:

            metadata = dict(
                doc.metadata or {}
            )

            metadata.update({
                "workflow_id": str(workflow_id),
                "source_file": source_file,
                "file_hash": file_hash,
                "page": metadata.get(
                    "page",
                    page_number,
                ),
                "file_type": "original",
                "language": original_language,
            })

            original_chunks.append({
                "page_content": doc.page_content,
                "metadata": metadata,
            })

        # -------------------------------------------------
        # Translated chunks
        # -------------------------------------------------

        translated_chunks = []

        if translated_text:

            translated_documents = chunk_text(
                text=translated_text,
                source_file=source_file,
                file_hash=file_hash,
                page_number=page_number,
                workflow_id=workflow_id,
                file_type="translated",
                language=translated_language,
            )

            for doc in translated_documents:

                metadata = dict(
                    doc.metadata or {}
                )

                metadata.update({
                    "workflow_id": str(workflow_id),
                    "source_file": source_file,
                    "file_hash": file_hash,
                    "page": metadata.get(
                        "page",
                        page_number,
                    ),
                    "file_type": "translated",
                    "language": translated_language,
                })

                translated_chunks.append({
                    "page_content": doc.page_content,
                    "metadata": metadata,
                })

        # -------------------------------------------------
        # Combine
        # -------------------------------------------------

        chunks = (
            original_chunks
            + translated_chunks
        )

        logger.info(
            f"[CHUNKING COMPLETED] "
            f"{workflow_id} | "
            f"original={len(original_chunks)} "
            f"translated={len(translated_chunks)} "
            f"total={len(chunks)}"
        )

        # -------------------------------------------------
        # Generate embeddings
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
            stage=WorkflowStage.CHUNKING,
            progress=50,
            error=str(e),
        )

        raise self.retry(
            exc=e,
            countdown=5,
        )

# =========================================================
# Translation Task
# =========================================================
@celery_app.task(
    bind=True,
    max_retries=3,
)
def translate_document_task(
    self,
    workflow_id: str,
    extracted_text: str,
    source_file: str,
    file_hash: str,
    page_number: int,
):

    try:

        logger.info(
            f"[TRANSLATION STARTED] {workflow_id}"
        )

        update_pipeline_status(
            workflow_id=workflow_id,
            status="TRANSLATING",
            stage=WorkflowStage.TRANSLATING,
            progress=25,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage=WorkflowStage.TRANSLATING,
            progress=25,
            message="Detecting language and translating if required...",
        )

        result = translation_service.process(
            workflow_id=workflow_id,
            text=extracted_text,
        )

        logger.info(
            f"[TRANSLATION COMPLETED] {workflow_id}"
        )

        # -------------------------------------------------
        # Chunk original + translated documents
        # -------------------------------------------------

        chunk_document_task.delay(
            workflow_id=workflow_id,
            original_text=extracted_text,
            translated_text=(
                result["text"]
                if result["translated"]
                else None
            ),
            original_language=result["language"],
            translated_language=
                result["target_language"] 
                if result["translated"] 
                else None,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
        )

    except Exception as e:

        logger.exception(
            "[TRANSLATION FAILED]"
        )

        emit_pipeline_failed(
            workflow_id=workflow_id,
            stage=WorkflowStage.TRANSLATING,
            progress=25,
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
            status="EMBEDDING",
            stage=WorkflowStage.EMBEDDING,
            progress=75,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage=WorkflowStage.EMBEDDING,
            progress=75,
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
            stage=WorkflowStage.EMBEDDING,
            progress=75,
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
            status="STORING",
            stage=WorkflowStage.STORING,
            progress=90,
        )

        emit_pipeline_stage(
            workflow_id=workflow_id,
            stage=WorkflowStage.STORING,
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
            stage=WorkflowStage.STORING,
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
        stage=WorkflowStage.COMPLETE,
        progress=100,
    )

    emit_pipeline_completed(
        workflow_id=workflow_id,
    )