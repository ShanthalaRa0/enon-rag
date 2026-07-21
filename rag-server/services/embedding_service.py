# services/embedding_service.py

import os
import logging

from dotenv import load_dotenv

from langchain_ollama import (
    OllamaEmbeddings,
)

from langchain_core.documents import (
    Document,
)

load_dotenv()

logger = logging.getLogger(__name__)


# =========================================================
# Embedding Model
# =========================================================

embeddings_model = OllamaEmbeddings(
    model=os.getenv(
        "EMBED_MODEL",
        "mxbai-embed-large",
    ),
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
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
        f"[EMBEDDING COMPLETED]"
    )

    return vectors