# services/retrieval_service.py

import logging

from search.hybrid_search import (
    hybrid_search,
)

logger = logging.getLogger(__name__)


# =========================================================
# Query Documents
# =========================================================

def query_documents(
    question: str,
    top_k: int = 5,
):
    """
    Retrieve relevant chunks using hybrid search.
    """

    try:

        logger.info(
            f"[QUERY] {question}"
        )

        results = hybrid_search(
            query=question,
            top_k=top_k,
        )

        logger.info(
            f"[RETRIEVAL COMPLETED] "
            f"{len(results)} chunks"
        )

        return results

    except Exception as e:

        logger.exception(
            "[RETRIEVAL FAILED]"
        )

        raise e