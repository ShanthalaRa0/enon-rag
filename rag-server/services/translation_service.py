import logging
from urllib import response

from services.database_service import database_service

from langchain_ollama import ChatOllama

from pathlib import Path

from lingua import (
    Language,
    LanguageDetectorBuilder,
)

from config.settings import (
    OLLAMA_BASE_URL,
    TRANSLATION_MODEL,
)

from config.paths import TRANSLATED_UPLOAD_DIR


logger = logging.getLogger(__name__)


class TranslationService:

    def __init__(self):

        self.detector = (
            LanguageDetectorBuilder
            .from_all_languages()
            .build()
        )

        self.llm = ChatOllama(
            model=TRANSLATION_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )


    # =====================================================
    # Detect Language
    # =====================================================

    def detect_language(
        self,
        text: str,
    ) -> str:

        language = self.detector.detect_language_of(text)

        if language is None:
            return "UNKNOWN"

        return language.name


    # =====================================================
    # Translate
    # =====================================================

    def translate(
        self,
        text: str,
        target_language: str,
    ) -> str:      

        prompt = f"""
You are a professional document translator.

Your task is to translate the ENTIRE document into exactly the specified target language.

TARGET LANGUAGE: {target_language}

The target language will ALWAYS be either:
- English
- Japanese

IMPORTANT:
- Output MUST be {target_language}
- Do NOT output Chinese.
- Do NOT output English except proper names, URLs, product names, technical identifiers, and numbers when appropriate.
- Do NOT summarize.
- Do NOT omit information.
- Do NOT add information that is not present in the original document.
- Preserve the original meaning as accurately as possible.
- Preserve paragraphs, headings, lists, tables, numbering, and structure where possible.
- Preserve names, numbers, dates, URLs, email addresses, and technical identifiers unless they should naturally be translated.
- Do not explain your translation.
- Return ONLY the translated document text.

Before producing the final answer, verify:
1. The entire document has been translated.
2. The output is written in exactly the TARGET LANGUAGE: {target_language}.
3. No unintended language appears in the output.

TARGET LANGUAGE: {target_language}

Document:

{text}
"""

        logger.info("[OLLAMA REQUEST START]")

        response = self.llm.invoke(prompt)

        logger.info("[OLLAMA RESPONSE RECEIVED]")

        logger.info(
            f"[OLLAMA RESPONSE TYPE] {type(response)}"
        )

        logger.info(
            f"[OLLAMA RESPONSE] {response}"
        )

        logger.info(
            f"[OLLAMA RESPONSE CONTENT TYPE] "
            f"{type(response.content)}"
        )

        logger.info(
            f"[OLLAMA RESPONSE CONTENT LENGTH] "
            f"{len(response.content) if response.content else 0}"
        )

        translated_text = response.content

        if not translated_text or not translated_text.strip():
            raise RuntimeError(
                "Ollama returned an empty translation response."
            )

        logger.info(
            f"[TRANSLATION OUTPUT] {translated_text[:500]}"
        )

        return translated_text


    # =====================================================
    # Save Translation
    # =====================================================

    def save_translation(
        self,
        translated_text: str,
        original_filename: str,
        target_language: str,
    ) -> str:

        original_path = Path(original_filename)

        translated_filename = (
            f"{original_path.stem}_translated_"
            f"{target_language.lower()}.txt"
        )

        translated_path = (
            TRANSLATED_UPLOAD_DIR /
            translated_filename
        )

        TRANSLATED_UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            f"[CHECK TRANSLATED FILE] {translated_path}"
        )

        translated_path.write_text(
            translated_text,
            encoding="utf-8",
        )

        logger.info(
            f"[TRANSLATION SAVED] {translated_path}"
        )

        return str(translated_path)


    # =====================================================
    # Process
    # =====================================================

    def process(
        self,
        workflow_id: str,
        text: str,
        original_filename: str,
    ) -> dict:

        language = self.detect_language(text)

        logger.info(
            f"[LANGUAGE DETECTED] {language}"
        )


        if language == Language.JAPANESE.name:

            target_language = "English"

        elif language == Language.ENGLISH.name:

            target_language = "Japanese"

        else:

            logger.info(
                "[NO TRANSLATION REQUIRED]"
            )

            return {
                "language": language,
                "text": text,
                "translated": False,
                "target_language": None,
                "translated_file": None,
            }

        logger.info(
            f"[TRANSLATION STARTED] "
            f"{language} -> {target_language}"
        )


        translated = self.translate(
            text=text,
            target_language=target_language,
        )


        translated_file = self.save_translation(
            translated_text=translated,
            original_filename=original_filename,
            target_language=target_language,
        )

        database_service.update_translation(
            workflow_id=workflow_id,
            original_language=language,
            translated=True,
            stored_filename=Path(translated_file).name,
        )
        


        logger.info(
            "[TRANSLATION COMPLETED]"
        )


        return {
            "language": language,
            "target_language": target_language,
            "text": translated,
            "translated": True,
            "translated_file": translated_file,
        }


translation_service = TranslationService()