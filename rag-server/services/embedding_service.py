# services/embedding_service.py

import logging

from langchain_ollama import OllamaEmbeddings

from config.settings import (
    EMBED_MODEL,
    OLLAMA_BASE_URL,
)

logger = logging.getLogger(__name__)


# =========================================================
# Embedding Model
# =========================================================

embeddings_model = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=OLLAMA_BASE_URL,
)

# =========================================================
# Return Model Instance
# =========================================================

def get_embedding_model():
    """
    Return embedding model instance.
    """

    return embeddings_model


# =========================================================
# Generate Embeddings
# =========================================================

def generate_embeddings(
    chunks: list,
):
    """
    Generate embeddings for chunked documents.
    """

    logger.info(
        f"[EMBEDDING] Processing {len(chunks)} chunks"
    )

    texts = [
        chunk["page_content"]
        for chunk in chunks
    ]

    vectors = embeddings_model.embed_documents(
        texts
    )

    logger.info(
        "[EMBEDDING COMPLETED]"
    )

    return vectors