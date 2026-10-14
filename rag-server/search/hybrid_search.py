# search/hybrid_search.py

import os
from search.bm25_search import normalize_text

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

    debug_vector_db(db, query)

    print("\n========== EXACT STRING TEST ==========")

    query_normalized = normalize_text(query).lower()

    for doc in db.docstore._dict.values():

        text = normalize_text(doc.page_content or "").lower()

        if query_normalized in text:
            print("EXACT MATCH FOUND")
            print("SOURCE:", doc.metadata.get("source_file"))
            print("TEXT:", doc.page_content[:500])

    print("=======================================\n")

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

    combined_results = reciprocal_rank_fusion(
    bm25_results,
    semantic_results,
)

    print(
        f"[SEARCH] Combined results: "
        f"{len(combined_results)}"
    )

    # -------------------------------------------------
    # Remove exact duplicate chunks
    # -------------------------------------------------

    unique_results = deduplicate_results(
        combined_results
    )

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
    Remove identical chunks while preserving different
    text passages from the same document page.
    """

    unique_results = []
    seen = set()

    for result in results:

        normalized_text = " ".join(
            str(result.get("text") or "").split()
        )

        key = (
            result.get("folder"),
            result.get("workflow_id"),
            result.get("filename"),
            result.get("file_type"),
            result.get("language"),
            normalized_text,
        )

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results


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

def debug_vector_db(db, search_text):

    print("\n========== VECTOR DB DEBUG ==========")

    print("DB PATH:", DB_PATH)

    print("FAISS VECTOR COUNT:", db.index.ntotal)

    print("DOCSTORE COUNT:", len(db.docstore._dict))

    search_text = normalize_text(search_text).lower()

    matches = []

    for doc_id, doc in db.docstore._dict.items():

        content = normalize_text(doc.page_content or "").lower()

        if search_text in content:

            matches.append(doc)

            print("\nMATCH FOUND")
            print("Document ID:", doc_id)
            print("Source:", doc.metadata.get("source_file"))
            print("Folder:", doc.metadata.get("folder"))
            print("Text:", content[:500])

    print("\nTOTAL EXACT MATCHES:", len(matches))

    print("=====================================\n")

def reciprocal_rank_fusion(
    bm25_results,
    semantic_results,
    k=60,
):
    fused = {}

    for result_list in [bm25_results, semantic_results]:

        for rank, result in enumerate(result_list, start=1):

            key = (
                result.get("folder"),
                result.get("workflow_id"),
                result.get("filename"),
                result.get("page"),
                result.get("file_type"),
                result.get("language"),
                " ".join(str(result.get("text") or "").split()),
            )

            if key not in fused:
                fused[key] = {
                    **result,
                    "rrf_score": 0.0,
                }

            fused[key]["rrf_score"] += 1.0 / (k + rank)

    return sorted(
        fused.values(),
        key=lambda x: x["rrf_score"],
        reverse=True,
    )