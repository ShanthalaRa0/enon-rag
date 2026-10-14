import json
import logging
import os
import re

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from search.hybrid_search import (
    deduplicate_results,
    hybrid_search,
)

load_dotenv()

logger = logging.getLogger(__name__)


# =========================================================
# LLM
# =========================================================

RAG_MODEL = os.getenv("RAG_MODEL", "qwen3.5:9b")
BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434",
)

llm = ChatOllama(
    model=RAG_MODEL,
    base_url=BASE_URL,
    temperature=0,
    reasoning=False,
    num_ctx=8192,
    num_predict=1024,
)


# =========================================================
# Generate Answer
# =========================================================

def generate_answer(
    question: str,
    results: list,
):
    """
    Give the user's question and retrieved documents
    to the LLM and generate the best answer.
    """

    if not results:
        return {
            "answer": (
                "I could not find relevant "
                "information in the provided documents."
            ),
            "sources": [],
        }

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_parts = []

    for index, result in enumerate(results):

        logger.info(
            "[RESULT %s] folder=%s filename=%s page=%s score=%s search_type=%s",
            index,
            result.get("folder"),
            result.get("filename"),
            result.get("page"),
            result.get("score"),
            result.get("search_type"),
        )

        logger.info(
            "[TEXT %s] %s",
            index,
            result.get("text", "")[:500],
        )

        context_parts.append(
            f"""
SOURCE {index + 1}

Filename:
{result.get("filename")}

Original filename:
{result.get("original_filename")}

Folder:
{result.get("folder", "documents")}

Page:
{result.get("page")}

Language:
{result.get("language")}

File type:
{result.get("file_type")}

Search type:
{result.get("search_type")}

Content:
{result.get("text", "")}
"""
        )

    context = "\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    prompt = f"""
Answer the user's question using only the document sources below.

QUESTION:
{question}

DOCUMENT SOURCES:
{context}

RULES:
1. Find the information that directly answers the question.
2. Check dates, transaction types, and amounts carefully.
3. Do not invent information.
4. If the requested transaction is absent but a different transaction
   is recorded on that date, explain the difference.
5. If the information is insufficient, say so.
6. Cite only the sources supporting your answer.
7. Keep your answer concise.

Return only valid JSON, without Markdown formatting:

{{
    "answer": "Your answer here",
    "source_indices": [1]
}}

Use the SOURCE numbers shown above.
"""

    # -----------------------------------------------------
    # Call LLM
    # -----------------------------------------------------

    logger.info("[LLM] Generating answer...")

    response = llm.invoke(prompt)

    logger.info(
        "[LLM DEBUG] response_metadata=%s",
        response.response_metadata,
    )

    logger.info(
        "[LLM DEBUG] usage_metadata=%s",
        response.usage_metadata,
    )

    logger.info(
        "[LLM DEBUG] additional_kwargs=%s",
        response.additional_kwargs,
    )

    logger.info(
        "[LLM DEBUG] content=%r",
        response.content,
    )

    logger.info(
        "[LLM DEBUG] reasoning_content=%r",
        getattr(response, "reasoning_content", None),
    )

    content = response.content.strip()

    logger.info(
        f"[LLM RAW RESPONSE] {content}"
    )

    # -----------------------------------------------------
    # Parse LLM response
    # -----------------------------------------------------

    answer = ""
    source_indices = []

    try:

        # Remove ```json ... ```
        content = re.sub(
            r"^```json\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"^```\s*",
            "",
            content,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

        parsed = json.loads(content)

        # Normal JSON object
        if isinstance(parsed, dict):

            answer = parsed.get(
                "answer",
                "",
            )

            source_indices = parsed.get(
                "source_indices",
                [],
            )

        # JSON returned as a JSON string
        elif isinstance(parsed, str):

            nested = json.loads(parsed)

            if isinstance(nested, dict):

                answer = nested.get(
                    "answer",
                    "",
                )

                source_indices = nested.get(
                    "source_indices",
                    [],
                )

            else:

                answer = parsed

        else:

            answer = str(parsed)

    except json.JSONDecodeError:

        logger.warning(
            "[LLM] Invalid JSON response"
        )

        answer = content
        source_indices = []

    # -----------------------------------------------------
    # Normalize answer
    # -----------------------------------------------------

    if isinstance(answer, dict):

        answer = answer.get(
            "answer",
            "",
        )

    if answer is None:

        answer = ""

    answer = str(answer).strip()

    # -----------------------------------------------------
    # Normalize source indices
    # -----------------------------------------------------

    if not isinstance(
        source_indices,
        list,
    ):

        source_indices = []

    # -----------------------------------------------------
    # Get source documents
    # -----------------------------------------------------

    sources = []

    for index in source_indices:

        try:

            result_index = int(index) - 1

            if not (
                0 <= result_index < len(results)
            ):
                continue

            result = results[
                result_index
            ]

            sources.append(
                {
                    "filename": result.get(
                        "filename"
                    ),
                    "original_filename": result.get(
                        "original_filename"
                    ),
                    "translated_filename": result.get(
                        "translated_filename"
                    ),
                    "workflow_id": result.get(
                        "workflow_id"
                    ),
                    "folder": result.get(
                        "folder",
                        "documents",
                    ),
                    "page": result.get(
                        "page"
                    ),
                    "file_type": result.get(
                        "file_type"
                    ),
                    "language": result.get(
                        "language"
                    ),
                }
            )

        except (
            ValueError,
            TypeError,
            IndexError,
        ):

            logger.warning(
                f"[LLM] Invalid source index: {index}"
            )

            continue

    logger.info(
        f"[LLM] Answer generated using "
        f"{len(sources)} sources"
    )

    return {
        "answer": answer,
        "sources": sources,
    }


# =========================================================
# Query Documents
# =========================================================

def query_documents(
    question: str,
    top_k: int = 5,
):
    """
    Retrieve relevant chunks using hybrid search
    and generate the best answer using the LLM.
    """

    try:

        logger.info(
            f"[QUERY] {question}"
        )

        # -------------------------------------------------
        # Hybrid Retrieval
        # -------------------------------------------------

        results = hybrid_search(
            query=question,
            top_k=top_k,
        )

        logger.info(
            f"[RETRIEVAL COMPLETED] "
            f"{len(results)} chunks"
        )

        # -------------------------------------------------
        # Remove duplicate sources
        # -------------------------------------------------

        results = deduplicate_results(
            results
        )

        logger.info(
            f"[DEDUPLICATION COMPLETED] "
            f"{len(results)} chunks"
        )

        # -------------------------------------------------
        # LLM Answer Generation
        # -------------------------------------------------

        llm_result = generate_answer(
            question=question,
            results=results,
        )

        logger.info(
            "[QUERY COMPLETED]"
        )

        return {
            "answer": llm_result[
                "answer"
            ],
            "sources": llm_result[
                "sources"
            ],
        }

    except Exception:

        logger.exception(
            "[RETRIEVAL FAILED]"
        )

        raise


# =========================================================
# Deduplicate Retrieval Results
# =========================================================

def deduplicate_results(
    results: list,
):
    """
    Remove duplicate retrieval results only when
    they refer to the same document and contain
    identical normalized text.

    Different chunks from the same page are preserved.
    """

    unique_results = []
    seen = set()

    for result in results:

        text = result.get("text", "")

        # Normalize whitespace to avoid false differences.
        normalized_text = " ".join(
            str(text).split()
        )

        key = (
            result.get("folder", "documents"),
            result.get("filename"),
            result.get("file_type"),
            result.get("language"),
            normalized_text,
        )

        if key in seen:

            logger.info(
                "[RETRIEVAL] Removing identical text chunk: "
                "folder=%s filename=%s page=%s",
                result.get("folder"),
                result.get("filename"),
                result.get("page"),
            )

            continue

        seen.add(key)
        unique_results.append(result)

    logger.info(
        "[RETRIEVAL] Deduplication: %s -> %s chunks",
        len(results),
        len(unique_results),
    )

    return unique_results