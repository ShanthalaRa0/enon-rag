# services/vector_store_service.py

import logging

from services.embedding_service import (
    get_embedding_model,
)

from langchain_core.documents import (
    Document,
)

from vectordb.faiss_store import (
    load_vector_db,
    create_vector_db,
    save_vector_db,
)


logger = logging.getLogger(__name__)


# =========================================================
# Duplicate Detection
# =========================================================

def document_exists(
    db,
    file_hash: str,
) -> bool:
    """
    Prevent duplicate ingestion.
    """

    if db is None:
        return False

    existing_hashes = set()

    for _, doc in db.docstore._dict.items():

        existing_hashes.add(
            doc.metadata.get("hash")
        )

    return file_hash in existing_hashes


# =========================================================
# Store Embeddings + Documents
# =========================================================

def store_embeddings(
    embeddings,
    chunks: list,
    metadata: dict = None,
):
    """
    Store chunked documents in FAISS.

    Celery sends chunks as dictionaries:
    
    {
        "page_content": "...",
        "metadata": {}
    }

    They are converted back to LangChain Documents.
    """

    try:

        logger.info(
            f"[VECTOR STORE] "
            f"storing {len(chunks)} chunks"
        )


        # -------------------------------------------------
        # Convert dict -> Document
        # -------------------------------------------------

        documents = []

        for chunk in chunks:

            document_metadata = {
                **chunk.get(
                    "metadata",
                    {}
                ),
                **(metadata or {}),
            }


            # Used for duplicate detection
            if metadata:

                document_metadata["hash"] = (
                    metadata.get(
                        "file_hash"
                    )
                )


            documents.append(
                Document(
                    page_content=chunk[
                        "page_content"
                    ],
                    metadata=document_metadata,
                )
            )


        # -------------------------------------------------
        # Load existing DB
        # -------------------------------------------------

        embedding_model = get_embedding_model()

        db = load_vector_db(
            embedding_model
        )


        # -------------------------------------------------
        # Duplicate detection
        # -------------------------------------------------

        file_hash = None

        if metadata:

            file_hash = metadata.get(
                "file_hash"
            )


        if file_hash and document_exists(
            db,
            file_hash,
        ):

            logger.warning(
                "[DUPLICATE DOCUMENT SKIPPED]"
            )

            return


        # -------------------------------------------------
        # Create / Append FAISS
        # -------------------------------------------------

        if db is None:

            logger.info(
                "[FAISS CREATE]"
            )

            embeddings = get_embedding_model()

            db = create_vector_db(
                documents,
                embeddings
            )


        else:

            logger.info(
                "[FAISS APPEND]"
            )


            db.add_documents(
                documents
            )


        # -------------------------------------------------
        # Save DB
        # -------------------------------------------------

        save_vector_db(
            db
        )


        logger.info(
            "[VECTOR STORE COMPLETED]"
        )


    except Exception:

        logger.exception(
            "[VECTOR STORE FAILED]"
        )

        raise