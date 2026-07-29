# search/semantic_search.py

def semantic_search(
    query,
    db,
    k=5,
    threshold=0.75,
):

    results = db.similarity_search_with_score(
        query,
        k=k,
    )

    filtered = []

    for doc, score in results:

        if score >= threshold:
            continue

        metadata = doc.metadata or {}

        filtered.append(
            {
                "filename": metadata.get(
                    "source_file"
                ),
                "workflow_id": metadata.get(
                    "workflow_id"
                ),
                "page": metadata.get(
                    "page"
                ),
                "file_type": metadata.get(
                    "file_type"
                ),
                "language": metadata.get(
                    "language"
                ),
                "score": float(score),
                "search_type": "semantic",
                "text": doc.page_content,
            }
        )

    return filtered[:k]