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

    # Retrieve more candidates than the final top_k
    candidate_k = max(top_k * 4, 20)

    print("\n[SEARCH] BM25...")

    bm25_results = bm25_search(
        query=query,
        db=db,
        k=candidate_k,
    )

    print(
        f"[SEARCH] BM25 returned "
        f"{len(bm25_results)} results"
    )

    print("\n[SEARCH] Semantic...")

    semantic_results = semantic_search(
        query=query,
        db=db,
        k=candidate_k,
    )

    print(
        f"[SEARCH] Semantic returned "
        f"{len(semantic_results)} results"
    )

    # -------------------------------------------------
    # Combine
    # -------------------------------------------------

    combined_results = (
        bm25_results +
        semantic_results
    )

    print(
        f"[SEARCH] Combined results: "
        f"{len(combined_results)}"
    )

    # -------------------------------------------------
    # Remove exact duplicate chunks
    # -------------------------------------------------

    unique_results = []

    seen = set()

    for result in combined_results:

        key = (
            result.get("folder"),
            result.get("workflow_id"),
            result.get("filename"),
            result.get("page"),
            result.get("text"),
        )

        if key in seen:
            continue

        seen.add(key)

        unique_results.append(result)

    print(
        f"[SEARCH] Unique chunks: "
        f"{len(unique_results)}"
    )

    # -------------------------------------------------
    # Diversify folders
    # -------------------------------------------------

    unique_results = diversify_by_folder(
        unique_results,
        max_per_folder=top_k,
    )

    print(
        f"[SEARCH] After folder diversification: "
        f"{len(unique_results)}"
    )

    # -------------------------------------------------
    # Final candidates
    # -------------------------------------------------

    return unique_results[:top_k]

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
            result.get("folder"),
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
            result.get("folder"),
            result.get("filename"),
            result.get("page"),
        )

        if key not in unique:
            unique[key] = result

    return list(unique.values())

from collections import defaultdict


def diversify_by_folder(
    results: list,
    max_per_folder: int = 2,
):
    folder_counts = {}
    diversified = []

    for result in results:

        folder = result.get(
            "folder",
            "documents",
        )

        count = folder_counts.get(
            folder,
            0,
        )

        if count >= max_per_folder:
            continue

        folder_counts[folder] = count + 1

        diversified.append(result)

    return diversified