# services/ingestion_pipeline.py

import logging

from services.chunking_service import (
    chunk_text,
)

from services.embedding_service import (
    generate_embeddings,
    get_embedding_model,
)

from services.vector_store_service import (
    document_exists,
    store_embeddings,
)

from vectordb.faiss_store import (
    load_vector_db,
)


logger = logging.getLogger(__name__)


# =========================================================
# Main Ingestion Pipeline
# =========================================================

def ingest_document(
    text: str,
    source_file: str,
    file_hash: str,
    page_number: int,
):
    """
    Full ingestion pipeline.

    Extracted Text
        ↓
    Chunking
        ↓
    Embedding
        ↓
    Vector Storage
    """

    try:

        logger.info(
            f"[INGESTION STARTED] "
            f"{source_file}"
        )

        # -------------------------------------------------
        # STEP 1 — CHUNKING
        # -------------------------------------------------

        chunked_docs = chunk_text(
            text=text,
            source_file=source_file,
            file_hash=file_hash,
            page_number=page_number,
        )

        logger.info(
            f"[CHUNKING COMPLETED] "
            f"{len(chunked_docs)} chunks"
        )

        # -------------------------------------------------
        # STEP 2 — EMBEDDINGS
        # -------------------------------------------------

        vectors = generate_embeddings(
            chunked_docs
        )

        logger.info(
            "[EMBEDDING COMPLETED]"
        )

        # -------------------------------------------------
        # STEP 3 — DUPLICATE CHECK
        # -------------------------------------------------

        embedding_model = get_embedding_model()

        db = load_vector_db(
            embedding_model
        )

        if document_exists(
            db,
            file_hash,
        ):

            logger.warning(
                f"[DUPLICATE DOCUMENT] "
                f"{source_file}"
            )

            return

        # -------------------------------------------------
        # STEP 4 — STORE
        # -------------------------------------------------

        store_embeddings(
            embeddings=vectors,
            chunks=chunked_docs,
            metadata={
                "file_hash": file_hash,
                "source_file": source_file,
                "page_number": page_number,
            }
        )

        logger.info(
            f"[INGESTION COMPLETED] "
            f"{source_file}"
        )

        return {
            "status": "SUCCESS",
            "chunks": len(chunked_docs),
        }

    except Exception as e:

        logger.exception(
            "[INGESTION FAILED]"
        )

        raise e