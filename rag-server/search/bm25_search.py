import os

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from fugashi import GenericTagger

load_dotenv()

tagger = GenericTagger(
    f"-r {os.getenv('MECABRC', '/etc/mecabrc')}"
)


def tokenize(text: str):

    return [
        word.surface.lower()
        for word in tagger(text)
        if word.surface.strip()
    ]


def bm25_search(
    query,
    db,
    k=5,
):

    docs = list(
        db.docstore._dict.values()
    )

    if not docs:
        return []

    corpus = [
        tokenize(
            doc.page_content
        )
        for doc in docs
    ]

    bm25 = BM25Okapi(
        corpus
    )

    tokenized_query = tokenize(
        query.lower()
    )

    if not tokenized_query:
        return []

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    results = []

    for doc, score in ranked:

        if score <= 0:
            continue

        metadata = doc.metadata or {}

        results.append(
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
                "search_type": "bm25",
                "text": doc.page_content,
            }
        )

        if len(results) >= k:
            break

    return results