from pathlib import Path

from docling.document_converter import DocumentConverter
from extractors.common import logger

converter = DocumentConverter()


def pdf_extract(file_path: Path) -> str:
    try:
        logger.info(
            f"[PDF EXTRACTION START] {file_path.name}"
        )

        conversion_result = converter.convert(file_path)

        extracted_text = (
            conversion_result.document.export_to_text()
        )

        logger.info(
            f"[PDF EXTRACTION COMPLETE] "
            f"Characters: {len(extracted_text)}"
        )

        logger.info(
            f"[PDF TEXT PREVIEW] "
            f"{extracted_text[:500]}"
        )

        if not extracted_text.strip():
            logger.warning(
                f"[PDF EMPTY] No text extracted from "
                f"{file_path.name}"
            )

        return extracted_text.strip()

    except Exception as e:
        logger.exception(
            f"[PDF EXTRACTION FAILED] {file_path.name}"
        )

        raise RuntimeError(
            f"PDF extraction failed: {e}"
        ) from e