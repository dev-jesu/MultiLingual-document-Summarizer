import re
from typing import List, Optional
from app.utils.token_estimator import estimate_tokens

def split_by_paragraph(text: str) -> List[str]:
    """
    Splits document text by paragraph boundaries (double newlines).
    
    Args:
        text (str): Full document text string.
        
    Returns:
        List[str]: List of paragraph text chunks.
    """
    if not text:
        return []
    # Split by two or more newlines
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    return paragraphs if paragraphs else ([text.strip()] if text.strip() else [])

def split_large_paragraph(paragraph: str, max_tokens: int, chars_per_token: float = 4.0) -> List[str]:
    """
    Splits an oversized paragraph into smaller chunks by sentence boundaries.
    Only used as a fallback if a single paragraph exceeds the maximum token limit.
    """
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_tokens = estimate_tokens(sentence, chars_per_token)
        
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def merge_small_chunks(
    chunks: List[str], 
    max_tokens: int = 6000, 
    overlap_tokens: int = 150,
    chars_per_token: float = 4.0
) -> List[str]:
    """
    Merges smaller text chunks into larger combined chunks up to max_tokens limit,
    with an optional token overlap between chunks to preserve context.
    
    Args:
        chunks (List[str]): List of candidate text chunks (e.g. paragraphs).
        max_tokens (int): Maximum estimated token capacity per combined chunk.
        overlap_tokens (int): Target number of tokens to overlap between sequential chunks.
        chars_per_token (float): Token estimation character ratio.
        
    Returns:
        List[str]: List of merged text chunks.
    """
    if not chunks:
        return []

    merged_chunks: List[str] = []
    current_chunk: List[str] = []
    current_token_count = 0

    for paragraph in chunks:
        paragraph_tokens = estimate_tokens(paragraph, chars_per_token)
        
        # If a single paragraph is too large, split it further
        if paragraph_tokens > max_tokens:
            # First, flush current buffer
            if current_chunk:
                merged_chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_token_count = 0
            
            sub_chunks = split_large_paragraph(paragraph, max_tokens, chars_per_token)
            merged_chunks.extend(sub_chunks[:-1])
            
            # The last sub_chunk becomes the start of the next buffer
            last_sub = sub_chunks[-1] if sub_chunks else ""
            if last_sub:
                current_chunk = [last_sub]
                current_token_count = estimate_tokens(last_sub, chars_per_token)
            continue

        if current_token_count + paragraph_tokens <= max_tokens:
            current_chunk.append(paragraph)
            current_token_count += paragraph_tokens
        else:
            # Buffer full, save it
            final_text = "\n\n".join(current_chunk)
            merged_chunks.append(final_text)
            
            # Calculate overlap from the end of the previous chunk
            overlap_text = ""
            if overlap_tokens > 0:
                # Approximate overlap by characters
                target_chars = int(overlap_tokens * chars_per_token)
                if len(final_text) > target_chars:
                    # Find a clean break point (newline or period) near the target
                    overlap_candidate = final_text[-target_chars:]
                    break_idx = max(overlap_candidate.find('\n'), overlap_candidate.find('. '))
                    if break_idx != -1:
                        overlap_text = overlap_candidate[break_idx:].strip()
                    else:
                        overlap_text = overlap_candidate.strip()
                else:
                    overlap_text = final_text
            
            # Start new buffer with overlap and current paragraph
            if overlap_text:
                current_chunk = [f"...{overlap_text}", paragraph]
            else:
                current_chunk = [paragraph]
                
            current_token_count = estimate_tokens("\n\n".join(current_chunk), chars_per_token)

    if current_chunk:
        merged_chunks.append("\n\n".join(current_chunk))

    return merged_chunks


# Alias for backward compatibility
split_by_paragraphs = split_by_paragraph


def chunk_document(
    text: str,
    pages_text: Optional[List[str]] = None,
    strategy: str = "merged",
    max_tokens: int = 6000,
    overlap: int = 150
) -> List[str]:
    """
    Unified entry point for chunking legal document text based on requested strategy.

    Args:
        text (str): Full document text string.
        pages_text (Optional[List[str]]): List of per-page raw texts if available.
        strategy (str): 'paragraph', 'page', or 'merged'.
        max_tokens (int): Max token threshold for merged chunks.
        overlap (int): Token overlap for sequential merged chunks.

    Returns:
        List[str]: Resulting text chunks.
    """
    if not text:
        return []

    if strategy == "page" and pages_text:
        return merge_small_chunks(pages_text, max_tokens=max_tokens, overlap_tokens=overlap)
    elif strategy == "paragraph":
        return split_by_paragraphs(text)
    else:  # "merged" (default)
        paragraphs = split_by_paragraphs(text)
        return merge_small_chunks(paragraphs, max_tokens=max_tokens, overlap_tokens=overlap)

