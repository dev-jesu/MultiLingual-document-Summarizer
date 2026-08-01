"""Dynamic translation prompt templates for legal summaries."""

from app.utils.language_utils import DEFAULT_LANGUAGE_LABELS


def build_translation_prompt(source_language: str, target_language: str, text: str) -> str:
    """Build a concise legal translation prompt for any supported language pair."""
    source_label = DEFAULT_LANGUAGE_LABELS.get(source_language, source_language)
    target_label = DEFAULT_LANGUAGE_LABELS.get(target_language, target_language)

    return f"""
Translate the following legal summary into natural, accurate {target_label}.
Preserve legal terminology, names of people and organizations, case numbers, dates, section numbers, court names, acts, and legal meaning.
Do not translate names or simplify the legal meaning.
Return only the translated text.

Source language: {source_label}
Text:
{text}
"""
