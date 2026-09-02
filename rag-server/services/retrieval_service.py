# services/retrieval_service.py

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


# LLM
llm = ChatOllama(
    model=os.getenv(
        "RAG_MODEL",
        "qwen2.5:7b",
    ),
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://host.docker.internal:11434",
    ),
    temperature=0,
    think=True,
)

# Generate Answer
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

    # Build context
    context_parts = []

    for index, result in enumerate(results):

        context_parts.append(
            f"""
SOURCE {index + 1}

Filename:
{result.get("filename")}

Original filename:
{result.get("original_filename")}

Page:
{result.get("page")}

Language:
{result.get("language")}

Search type:
{result.get("search_type")}

Content:
{result.get("text", "")}
"""
        )
    context = "\n".join(
        context_parts
    )

    # Prompt
    prompt = f"""
You are an expert RAG question-answering system.

You must answer the user's question using ONLY the
information contained in the retrieved document sources.

USER QUESTION:
{question}

RETRIEVED SOURCES:
{context}

INSTRUCTIONS:

1. Read all retrieved sources carefully.
2. Determine which sources are relevant to the question.
3. Discard irrelevant information.
4. Do not assume that the highest BM25 or semantic
   score is necessarily the correct answer.
5. Compare the actual content of the sources.
6. If multiple sources contain useful information,
   combine them into one accurate answer.
7. Remove duplicate information.
8. Do NOT invent information.
9. Do NOT use your general knowledge when the answer
   is not present in the retrieved sources.
10. If the retrieved sources do not contain enough
    information to answer the question, say:
    "I could not find enough information in the
    provided documents to answer this question."
11. Give a clear and concise answer.
12. Identify which sources were used to construct
    the answer.
13. Do not cite multiple sources if they contain substantially
    the same information.
14. Prefer the smallest set of sources necessary to support
    the answer.
15. If SOURCE 2 repeats SOURCE 1, do not include SOURCE 2
    unless it provides additional information.
16. Prefer one strong source over several redundant sources.
Return ONLY valid JSON in this format:
{{
    "answer": "The final answer to the user's question.",
    "source_indices": [1, 3]
}}

The source_indices must contain the SOURCE numbers
that actually support the answer.
"""

    # Call LLM
    logger.info("[LLM] Generating answer...")

    response = llm.invoke(prompt)

    content = response.content.strip()

    logger.info(f"[LLM RAW RESPONSE] {content}")

    # Parse LLM response

    answer = ""
    source_indices = []

    try:
        # Remove ```json ... ``` if the model adds it
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

      
        # Handle normal JSON object
        #
        # {
        #   "answer": "...",
        #   "source_indices": [1, 5]
        # }


        if isinstance(parsed, dict):

            answer = parsed.get(
                "answer",
                "",
            )

            source_indices = parsed.get(
                "source_indices",
                [],
            )

       
        # Handle JSON returned as a JSON string
        #
        # "{\"answer\":\"...\",\"source_indices\":[1,5]}"

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

    # Normalize answer

    if isinstance(answer, dict):

        answer = answer.get(
            "answer",
            "",
        )

    if answer is None:

        answer = ""

    answer = str(answer).strip()

    # Normalize source indices

    if not isinstance(
        source_indices,
        list,
    ):

        source_indices = []


    # Get source documents

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



# Query Documents
def query_documents(
    question: str,
    top_k: int = 5,
):
    """
    Retrieve relevant chunks using hybrid searchgenerate_answer
    and generate the best answer using the LLM.
    """

    try:

        logger.info(f"[QUERY] {question}")

        # Hybrid Retrieval
        results = hybrid_search(query=question,top_k=top_k)

        logger.info(f"[RETRIEVAL COMPLETED] " f"{len(results)} chunks")

        # Remove duplicate sources
        results = deduplicate_results(results)

        # LLM Answer Generation
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
    except Exception as e:
        logger.exception("[RETRIEVAL FAILED]")
        raise


def deduplicate_results(results: list):
    """
    Remove duplicate retrieval results based on:
    filename + page + file_type + language.

    When duplicates are found, the first result is kept.
    Since hybrid_search returns results by relevance,
    the first result should be the highest-ranked one.
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

            logger.info(
                "[RETRIEVAL] Removing duplicate result: "
                f"filename={key[0]}, "
                f"page={key[1]}, "
                f"file_type={key[2]}, "
                f"language={key[3]}"
            )

            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results