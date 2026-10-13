# search/semantic_search.py

def semantic_search(
    query,
    db,
    k=50,
    threshold=None
):

    results = db.similarity_search_with_score(
        query,
        k=k,
    )

    print("\nSEMANTIC SEARCH DEBUG")
    print("Query:", query)
    print("Results:", len(results))

    filtered = []

    for doc, score in results:

        print(
            "Distance:", float(score),
            "Source:", doc.metadata.get("source_file"),
            "Text:", doc.page_content[:200],
        )

        if threshold is not None and score >= threshold:
            continue

        metadata = doc.metadata or {}

        filtered.append(
            {
                "filename": metadata.get("source_file"),
                "workflow_id": metadata.get("workflow_id"),
                "folder": metadata.get("folder"),
                "page": metadata.get("page"),
                "file_type": metadata.get("file_type"),
                "language": metadata.get("language"),
                "score": float(score),
                "search_type": "semantic",
                "text": doc.page_content,
            }
        )

    return filtered[:k]

def semantic_searchOld(
    query,
    db,
    k=50,
    threshold=0.85
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
                "folder": metadata.get(
                    "folder"
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