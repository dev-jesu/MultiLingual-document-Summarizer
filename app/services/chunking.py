from typing import Optional
from app.utils.token_estimator import estimate_tokens


def split_by_pages(pages_text: list[str]) -> list[str]:
    """
    Splits text into chunks corresponding to document pages.
    
    Args:
        pages_text (list[str]): List of raw page texts.
        
    Returns:
        list[str]: Filtered list of non-empty page text chunks.
    """
    return [page.strip() for page in pages_text if page and page.strip()]


def split_by_paragraphs(text: str) -> list[str]:
    """
    Splits document text by paragraph boundaries.
    
    Args:
        text (str): Full document text string.
        
    Returns:
        list[str]: List of paragraph text chunks.
    """
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs if paragraphs else ([text.strip()] if text.strip() else [])


def merge_small_chunks(
    chunks: list[str], 
    max_tokens: int = 8000, 
    chars_per_token: float = 4.0
) -> list[str]:
    """
    Merges smaller text chunks into larger combined chunks up to max_tokens limit.
    
    Useful for bundling pages or paragraphs into context windows for LLM processing.
    
    Args:
        chunks (list[str]): List of candidate text chunks.
        max_tokens (int): Maximum estimated token capacity per combined chunk.
        chars_per_token (float): Token estimation character ratio.
        
    Returns:
        list[str]: List of merged text chunks.
    """
    if not chunks:
        return []

    merged_chunks: list[str] = []
    current_chunk: list[str] = []
    current_token_count = 0

    for chunk in chunks:
        chunk_tokens = estimate_tokens(chunk, chars_per_token)
        
        # If single chunk itself exceeds max_tokens, store current accumulated and add large chunk directly
        if chunk_tokens >= max_tokens:
            if current_chunk:
                merged_chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_token_count = 0
            merged_chunks.append(chunk)
            continue

        if current_token_count + chunk_tokens <= max_tokens:
            current_chunk.append(chunk)
            current_token_count += chunk_tokens
        else:
            merged_chunks.append("\n\n".join(current_chunk))
            current_chunk = [chunk]
            current_token_count = chunk_tokens

    if current_chunk:
        merged_chunks.append("\n\n".join(current_chunk))

    return merged_chunks
