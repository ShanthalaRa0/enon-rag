# search/hybrid_search.py

import os

from dotenv import load_dotenv

from langchain_community.vectorstores import (
    FAISS,
)

from services.embedding_service import (
    get_embedding_model,
)

from search.bm25_search import (
    bm25_search,
)

from search.semantic_search import (
    semantic_search,
)

load_dotenv()

BASE_DIR = os.path.dirname(__file__)

DB_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        os.getenv(
            "DB_PATH",
            "vector_store",
        ),
    )
)


def load_db():
    """
    Load FAISS database.
    """

    embeddings = get_embedding_model()

    return FAISS.load_local(
        DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def hybrid_search(
    query,
    top_k=5,
):

    db = load_db()

    print(
        "\n[SEARCH] BM25..."
    )

    bm25_results = bm25_search(
        query=query,
        db=db,
        k=top_k,
    )

    print(
        f"[SEARCH] BM25 returned "
        f"{len(bm25_results)} results"
    )

    # semantic search
    semantic_results = semantic_search(
        query=query,
        db=db,
        k=top_k,
    )

    print(
        f"[SEARCH] Semantic returned "
        f"{len(semantic_results)} results"
    )

    # combine results
    combined_results = bm25_results + semantic_results

    # remove duplicates
    unique_results = []

    seen = set()

    for result in combined_results:

        # Prefer workflow/page/text as identity
        key = (
            result.get("workflow_id"),
            result.get("filename"),
            result.get("page"),
            result.get("text"),
        )

        if key in seen:
            continue

        seen.add(key)

        unique_results.append(
            result
        )

    print(
        f"[SEARCH] Combined unique results: "
        f"{len(unique_results)}"
    )
    unique_results = deduplicate_results(unique_results)
    unique_results = deduplicate_by_document_page(unique_results)
  
    # RETURN CANDIDATES
    return unique_results  

def deduplicate_results(results: list):
    """
    Remove duplicate search results based on:
    filename + page + file_type + language.

    The first result is kept.
    """

    unique_results = []
    seen = set()

    for result in results:

        key = (
            result.get("filename"),
            result.get("page"),
            result.get("file_type"),
            result.get("language"),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results

def deduplicate_by_document_page(results: list):
    unique = {}

    for result in results:
        key = (
            result.get("filename"),
            result.get("page"),
        )

        if key not in unique:
            unique[key] = result

    return list(unique.values())