"""Dynamic prompt definitions for multilingual legal summarization."""

from app.utils.language_utils import DEFAULT_LANGUAGE_LABELS


def build_summary_prompt(target_language: str, text: str) -> str:
    """Build a concise legal summary prompt for any supported target language."""
    target_label = DEFAULT_LANGUAGE_LABELS.get(target_language, target_language)
    return f"""
You are an expert legal assistant summarizing Indian court documents.
Summarize the document in concise, professional {target_label}.

Preserve the following if present:
- Parties involved
- Case facts
- Important dates
- Court observations
- Legal issues
- Acts or sections mentioned
- Final judgment
- Relief granted or denied

Rules:
- Preserve legal meaning.
- Do not invent facts.
- Do not simplify legal meaning.
- Return only the summary text.

Document Text:
{text}
"""
