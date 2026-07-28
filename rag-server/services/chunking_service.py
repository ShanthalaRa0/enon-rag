
import os

from dotenv import load_dotenv

from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

def clean_text(text: str) -> str:
    """
    Normalize extracted text.
    """

    return (
        text.replace("\n", " ")
        .replace("  ", " ")
        .strip()
    )


def create_document(
    text: str,
    source_file: str,
    file_hash: str,
    page_number: int,
) -> Document:
    """
    Create LangChain document object.
    """

    return Document(
        page_content=clean_text(text),
        metadata={
            "source": source_file,
            "hash": file_hash,
            "page": page_number,
        },
    )


def chunk_document(
    document: Document,
) -> list[Document]:
    """
    Split document into chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(
        [document]
    )

def chunk_text(
    text: str,
    source_file: str = "unknown",
    file_hash: str = "unknown",
    page_number: int = 1,
):
    """
    Orchestration-compatible wrapper.

    Converts raw text into LangChain chunks.
    """

    document = create_document(
        text=text,
        source_file=source_file,
        file_hash=file_hash,
        page_number=page_number,
    )

    chunks = chunk_document(document)

    return chunks