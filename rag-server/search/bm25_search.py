
import os
import re
import unicodedata
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from fugashi import GenericTagger

load_dotenv()

tagger = GenericTagger(f"-r {os.getenv('MECABRC', '/etc/mecabrc')}")

def normalize_text(text: str) -> str:
    """Normalize Unicode (e.g. １ -> 1, ＣＨ -> CH) and standardize Katakana variations."""
    if not text:
        return ""
    # Convert full-width ASCII/numbers to half-width, standardizing NFKC
    text = unicodedata.normalize("NFKC", str(text))
    # Normalize common Japanese spelling variations (e.g. チャネル -> チャンネル)
    text = text.replace("チャネル", "チャンネル")
    return text

def tokenize(text: str) -> list:
    if not text:
        return []

    text = normalize_text(text)

    # 1. MeCab Tokenization
    mecab_tokens = [
        word.surface.lower()
        for word in tagger(text)
        if word.surface.strip()
    ]

    # 2. Extract alphanumeric sub-tokens
    ascii_tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", text)
    ]

    # Combine while avoiding artificial double-counting
    seen_mecab = set(mecab_tokens)
    extra_ascii = [t for t in ascii_tokens if t not in seen_mecab]

    return mecab_tokens + extra_ascii

def tokenizeOld(text: str):
    if not text:
        return []

    text = normalize_text(text)

    # 1. MeCab Tokenization
    mecab_tokens = [
        word.surface.lower()
        for word in tagger(text)
        if word.surface.strip()
    ]

    # 2. Extract alphanumeric sub-tokens to guarantee ASCII matches (e.g., EMS, PCB, 1)
    ascii_tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", text)
    ]

    # 3. Combine without deduplication to preserve TF (Term Frequency) for BM25
    tokens = [t for t in (mecab_tokens + ascii_tokens) if t.strip()]

    return tokens


def bm25_search(
    query,
    db,
    k=5,
):
    docs = list(db.docstore._dict.values())

    if not docs:
        return []

    corpus = [
        tokenize(doc.page_content or "")
        for doc in docs
    ]

    bm25 = BM25Okapi(corpus)

    tokenized_query = tokenize(query)

    print("BM25 QUERY:", query)
    print("BM25 TOKENS:", tokenized_query)
    print("BM25 DOCS:", len(docs))
    print("BM25 CORPUS:", len(corpus))

    scores = bm25.get_scores(tokenized_query)

    # DEBUG: print every positive EMS match
    print("BM25 POSITIVE MATCHES:")

    for doc, score in zip(docs, scores):
        if score > 0:
            print(
                "score=",
                float(score),
                "folder=",
                doc.metadata.get("folder"),
                "source=",
                doc.metadata.get("source_file"),
                "contains_ems=",
                "ems" in tokenize(doc.page_content or ""),
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

        # IMPORTANT:
        # Do not filter score <= 0 here while debugging.
        metadata = doc.metadata or {}

        results.append(
            {
                "filename": metadata.get("source_file"),
                "original_filename": metadata.get(
                    "original_filename"
                ),
                "translated_filename": metadata.get(
                    "stored_filename"
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
                "search_type": "bm25",
                "text": doc.page_content,
            }
        )

        if len(results) >= k:
            break

    return results