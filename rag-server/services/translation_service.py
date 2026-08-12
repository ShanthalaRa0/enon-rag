import logging

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
You are a professional translator.

Translate the following document into {target_language}.

Rules:

- Translate everything.
- Do NOT summarize.
- Do NOT omit information.
- Preserve the meaning.
- Preserve formatting where possible.
- Return ONLY the translated text.

Document:

{text}
"""

        logger.info("[OLLAMA REQUEST START]")

        response = self.llm.invoke(prompt)

        logger.info("[OLLAMA RESPONSE RECEIVED]")

        translated_text = response.content

        logger.info(
            f"[TRANSLATION OUTPUT] {translated_text[:200]}"
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