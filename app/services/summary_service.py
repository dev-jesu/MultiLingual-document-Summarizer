import time
from typing import Dict, Any

from app.config import settings
from app.utils.logger import logger
from app.utils.token_estimator import estimate_tokens
from app.services.cleaner import clean_legal_text
from app.services.chunking import split_by_paragraph, merge_small_chunks
from app.services.gemini_service import generate_content_with_retry
from app.prompts.summary_prompt import LEGAL_SINGLE_PASS_PROMPT, LEGAL_CHUNK_PROMPT, LEGAL_COMBINE_PROMPT

class SummaryService:
    @staticmethod
    def summarize_document(filename: str, raw_text: str, pages: int = None) -> Dict[str, Any]:
        """
        Orchestrates the entire document summarization pipeline:
        1. Cleans text.
        2. Estimates tokens.
        3. Decides between single-pass vs. chunked summarization.
        4. Calls Gemini API.
        5. Returns structured metadata and final summary.
        """
        start_time = time.perf_counter()
        
        logger.info(f"Starting summarization pipeline for {filename}")
        
        # 1. Clean Text
        cleaned_text = clean_legal_text(raw_text)
        
        # 2. Estimate Tokens
        total_tokens = estimate_tokens(cleaned_text)
        logger.info(f"File: {filename} | Estimated Tokens: {total_tokens}")
        
        gemini_requests = 0
        chunks_processed = 0
        
        # 3. Decision Logic
        if total_tokens <= settings.MAX_INPUT_TOKENS:
            # Single-pass summarization
            logger.info("Token count within limits. Using single-pass summarization.")
            chunks_processed = 1
            gemini_requests = 1
            final_summary = generate_content_with_retry(LEGAL_SINGLE_PASS_PROMPT, cleaned_text)
        else:
            # Chunked summarization
            logger.info("Token count exceeds limit. Initiating chunking pipeline.")
            
            # Split into paragraphs, then merge into optimally sized chunks
            paragraphs = split_by_paragraph(cleaned_text)
            chunks = merge_small_chunks(
                chunks=paragraphs,
                max_tokens=settings.MAX_INPUT_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP
            )
            
            chunks_processed = len(chunks)
            logger.info(f"Document split into {chunks_processed} chunks.")
            
            chunk_summaries = []
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"Processing chunk {i}/{chunks_processed}...")
                chunk_summary = generate_content_with_retry(LEGAL_CHUNK_PROMPT, chunk)
                chunk_summaries.append(chunk_summary)
                gemini_requests += 1
                
            combined_summaries_text = "\n\n---\n\n".join(chunk_summaries)
            
            # Check if combined summaries are still too large (rare, but possible for huge docs)
            combined_tokens = estimate_tokens(combined_summaries_text)
            if combined_tokens > settings.MAX_INPUT_TOKENS:
                logger.warning("Combined chunk summaries exceed limit. Performing recursive reduction. (Not fully implemented, doing single pass fallback)")
                # In a more robust system, we would recursively chunk the summaries here.
                # For Stage 2, we assume the combined summaries will fit in a single prompt for most cases.
                # We will attempt one final reduction pass.
            
            logger.info("Combining chunk summaries into final summary.")
            final_summary = generate_content_with_retry(LEGAL_COMBINE_PROMPT, combined_summaries_text)
            gemini_requests += 1

        end_time = time.perf_counter()
        processing_time = round(end_time - start_time, 2)
        
        logger.info(f"Summarization complete for {filename}. Time: {processing_time}s | API Requests: {gemini_requests}")
        
        return {
            "filename": filename,
            "pages": pages,
            "estimated_tokens": total_tokens,
            "chunks_processed": chunks_processed,
            "gemini_requests": gemini_requests,
            "processing_time_seconds": processing_time,
            "summary": final_summary
        }
