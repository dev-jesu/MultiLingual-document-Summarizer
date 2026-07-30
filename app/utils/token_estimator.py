def estimate_tokens(text: str, chars_per_token: float = 4.0) -> int:
    """
    Provider-independent token estimator.
    
    Estimates token count based on character length heuristics. Standard rule of thumb
    for English legal text is ~4 characters per token.
    
    Args:
        text (str): Input text string.
        chars_per_token (float): Average characters per token ratio (default: 4.0).
        
    Returns:
        int: Estimated number of tokens.
    """
    if not text:
        return 0
        
    # Heuristic ratio: len(text) / chars_per_token
    estimated = int(len(text) / chars_per_token)
    return max(1, estimated)
