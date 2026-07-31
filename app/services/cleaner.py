import re

def clean_legal_text(text: str) -> str:
    """
    Cleans extracted legal text by normalizing spaces and line breaks,
    while carefully preserving legal numbering, citations, and structure.
    
    Args:
        text (str): Raw extracted text.
        
    Returns:
        str: Cleaned text suitable for chunking and summarization.
    """
    if not text:
        return ""

    # Normalize multiple spaces (excluding newlines)
    cleaned = re.sub(r'[ \t]+', ' ', text)

    # Normalize multiple blank lines to a maximum of two (paragraph break)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Remove common page artifacts (e.g., "Page 1 of 10" on its own line)
    # This regex looks for lines that only contain page numbering.
    cleaned = re.sub(r'(?im)^[\s-]*page\s+\d+(\s+of\s+\d+)?[\s-]*$', '', cleaned)

    # Remove common legal document watermarks and boilerplate on standalone lines
    boilerplate_patterns = [
        r'(?im)^\s*strictly\s+confidential\s*$',
        r'(?im)^\s*confidential\s*$',
        r'(?im)^\s*draft\s*$',
        r'(?im)^\s*not\s+for\s+circulation\s*$',
        r'(?im)^\s*privileged\s+and\s+confidential\s*$',
    ]
    for pattern in boilerplate_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Remove standalone numbers that might be just page numbers at the bottom/top,
    # but be very careful not to remove numbered lists. A page number is usually
    # surrounded by blank lines. We can safely trim leading/trailing whitespace.
    
    # Fix broken line breaks within sentences. 
    # If a line ends with a lower case letter and the next line starts with a lower case letter,
    # they likely belong to the same sentence.
    # Note: This is a simplistic heuristic and might need refinement for complex legal texts.
    cleaned = re.sub(r'([a-z,])\n([a-z])', r'\1 \2', cleaned)

    return cleaned.strip()
