import time
from typing import Dict, Any, Optional

from app.config import settings
from app.utils.logger import logger
from app.utils.token_estimator import estimate_tokens
from app.services.cleaner import clean_legal_text
from app.services.chunking import split_by_paragraph, merge_small_chunks
from app.services.gemini_service import generate_content_with_retry
from app.prompts.summary_prompt import build_summary_prompt
from app.services.language_detection import (
    MixedLanguageError,
    UnsupportedLanguageError,
    detect_language,
    normalize_language_parameters,
)
from app.services.translation_service import TranslationService


class SummaryService:
    @staticmethod
    def summarize_document(
        filename: str,
        raw_text: str,
        pages: int = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrates the document summarization pipeline with optional multilingual support.
        """
        start_time = time.perf_counter()

        logger.info(f"Starting summarization pipeline for {filename}")

        cleaned_text = clean_legal_text(raw_text)
        total_tokens = estimate_tokens(cleaned_text)
        logger.info(f"File: {filename} | Estimated Tokens: {total_tokens}")

        source_language, target_language = normalize_language_parameters(
            source_language=source_language or settings.DEFAULT_SOURCE_LANGUAGE,
            target_language=target_language or settings.DEFAULT_TARGET_LANGUAGE,
        )

        if source_language == "auto":
            detected_language = detect_language(cleaned_text)
        else:
            detected_language = source_language

        logger.info(
            f"File: {filename} | Source language requested={source_language} | Detected={detected_language} | Target={target_language}"
        )

        summary_prompt = build_summary_prompt(target_language, "{text}")

        gemini_requests = 0
        chunks_processed = 0

        if total_tokens <= settings.MAX_INPUT_TOKENS:
            logger.info("Token count within limits. Using single-pass summarization.")
            chunks_processed = 1
            gemini_requests = 1
            final_summary = generate_content_with_retry(summary_prompt.format(text=cleaned_text), cleaned_text)
        else:
            logger.info("Token count exceeds limit. Initiating chunking pipeline.")

            paragraphs = split_by_paragraph(cleaned_text)
            chunks = merge_small_chunks(
                chunks=paragraphs,
                max_tokens=settings.MAX_INPUT_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP,
            )

            chunks_processed = len(chunks)
            logger.info(f"Document split into {chunks_processed} chunks.")

            chunk_summaries = []
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"Processing chunk {i}/{chunks_processed}...")
                chunk_summary = generate_content_with_retry(summary_prompt.format(text=chunk), chunk)
                chunk_summaries.append(chunk_summary)
                gemini_requests += 1

            combined_summaries_text = "\n\n---\n\n".join(chunk_summaries)
            combined_tokens = estimate_tokens(combined_summaries_text)
            if combined_tokens > settings.MAX_INPUT_TOKENS:
                logger.warning("Combined chunk summaries exceed limit. Performing single-pass fallback.")

            logger.info("Combining chunk summaries into final summary.")
            final_summary = generate_content_with_retry(summary_prompt.format(text=combined_summaries_text), combined_summaries_text)
            gemini_requests += 1

        if detected_language != target_language:
            logger.info("Translation stage: summary translation requested.")
            final_summary = TranslationService.translate_summary(
                text=final_summary,
                source_language=detected_language,
                target_language=target_language,
            )
            gemini_requests += 1

        end_time = time.perf_counter()
        processing_time = round(end_time - start_time, 2)

        logger.info(
            f"Summarization complete for {filename}. Time: {processing_time}s | API Requests: {gemini_requests}"
        )

        return {
            "filename": filename,
            "pages": pages,
            "estimated_tokens": total_tokens,
            "chunks_processed": chunks_processed,
            "gemini_requests": gemini_requests,
            "processing_time_seconds": processing_time,
            "summary": final_summary,
        }
