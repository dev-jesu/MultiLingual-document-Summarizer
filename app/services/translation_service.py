import time
from typing import Optional

from app.config import settings
from app.prompts.translation_prompt import build_translation_prompt
from app.services.gemini_service import generate_content_with_retry
from app.utils.logger import logger


class TranslationService:
    @staticmethod
    def translate_summary(
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate a legal summary from one supported language to another."""
        if not text or not text.strip():
            raise ValueError("Translation text is empty.")

        if source_language == target_language:
            return text.strip()

        prompt = build_translation_prompt(source_language, target_language, "{text}")

        start_time = time.perf_counter()
        logger.info(
            "Translation stage: %s -> %s | processing_time=%s",
            source_language,
            target_language,
            "started",
        )
        translated = generate_content_with_retry(prompt, text)
        elapsed = round(time.perf_counter() - start_time, 2)

        if not translated or not translated.strip():
            raise RuntimeError("Translation returned an empty result.")

        logger.info(
            "Translation stage completed: %s -> %s | processing_time_seconds=%.2f",
            source_language,
            target_language,
            elapsed,
        )
        return translated.strip()
