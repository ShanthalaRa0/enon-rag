# services/chunking_service.py

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
    workflow_id: str,
    file_type: str,
    language: str,
) -> Document:

    return Document(
        page_content=clean_text(text),
        metadata={
            "source": source_file,
            "source_file": source_file,
            "hash": file_hash,
            "file_hash": file_hash,
            "page": page_number,
            "workflow_id": workflow_id,
            "file_type": file_type,
            "language": language,
        },
    )


def chunk_document(
    document: Document,
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(
        [document]
    )


def chunk_text(
    text: str,
    source_file: str,
    file_hash: str,
    page_number: int,
    workflow_id: str,
    file_type: str,
    language: str,
):
    document = create_document(
        text=text,
        source_file=source_file,
        file_hash=file_hash,
        page_number=page_number,
        workflow_id=workflow_id,
        file_type=file_type,
        language=language,
    )

    return chunk_document(document)