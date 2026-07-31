def estimate_tokens(text: str, chars_per_token: float = 4.0) -> int:
    """
    Fast, provider-independent token count estimator based on character length heuristics.
    
    Standard rule of thumb for English legal text is ~4 characters per token.
    
    Args:
        text (str): Input text string.
        chars_per_token (float): Average characters per token ratio (default: 4.0).
        
    Returns:
        int: Estimated number of tokens.
    """
    if not text:
        return 0
    estimated = int(len(text) / chars_per_token)
    return max(1, estimated)

def estimate_word_count(text: str) -> int:
    """
    Calculates word count of a text string.
    """
    if not text:
        return 0
    return len(text.split())
