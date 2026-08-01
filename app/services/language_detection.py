import re
from typing import Optional

from app.config import settings
from app.utils.language_utils import parse_supported_languages, normalize_language_code

SUPPORTED_LANGUAGES = parse_supported_languages(settings.SUPPORTED_LANGUAGES)
SUPPORTED_LANGUAGE_CODES = set(SUPPORTED_LANGUAGES.keys())


class UnsupportedLanguageError(ValueError):
    """Raised when the provided or detected language is unsupported."""


class MixedLanguageError(UnsupportedLanguageError):
    """Raised when a document appears to contain mixed-language text."""


def normalize_language_parameters(source_language: Optional[str], target_language: Optional[str]) -> tuple[str, str]:
    """Validate and normalize requested source/target language parameters."""
    source = (source_language or "auto").strip().lower()
    target = (target_language or settings.DEFAULT_TARGET_LANGUAGE).strip().lower()

    if source not in {"auto", *SUPPORTED_LANGUAGE_CODES}:
        raise UnsupportedLanguageError(
            f"Unsupported source language '{source_language}'. Supported values are: auto, {', '.join(sorted(SUPPORTED_LANGUAGE_CODES))}."
        )

    if target not in SUPPORTED_LANGUAGE_CODES:
        raise UnsupportedLanguageError(
            f"Unsupported target language '{target_language}'. Supported values are: {', '.join(sorted(SUPPORTED_LANGUAGE_CODES))}."
        )

    return source, target


def detect_language(text: str, preferred_language: Optional[str] = None) -> str:
    """Detect the document's language using lightweight heuristics."""
    if preferred_language:
        normalized = preferred_language.strip().lower()
        if normalized == "auto":
            return detect_language(text)
        normalized_code = normalize_language_code(normalized, SUPPORTED_LANGUAGES)
        if normalized_code is None:
            raise UnsupportedLanguageError(
                f"Unsupported source language '{preferred_language}'. Supported values are: auto, {', '.join(sorted(SUPPORTED_LANGUAGE_CODES))}."
            )
        return normalized_code

    if not text or not text.strip():
        raise UnsupportedLanguageError("Input text is empty. Please provide a document with supported content.")

    scripts = {
        "en": re.compile(r"[A-Za-z]"),
        "ta": re.compile(r"[\u0B80-\u0BFF]"),
        "hi": re.compile(r"[\u0900-\u097F]"),
        "te": re.compile(r"[\u0C00-\u0C7F]"),
        "kn": re.compile(r"[\u0C80-\u0CFF]"),
        "ml": re.compile(r"[\u0D00-\u0D7F]"),
        "mr": re.compile(r"[\u0900-\u097F]"),
    }

    detected_scripts = [code for code, pattern in scripts.items() if pattern.search(text)]

    if not detected_scripts:
        raise UnsupportedLanguageError("Unsupported language. Only English and the supported Indian languages are supported.")

    if "hi" in detected_scripts and "mr" in detected_scripts:
        if any(token in text for token in ["आहे", "असले", "प्रकरणात", "न्यायालयाने", "दिला"]):
            return "mr"
        return "hi"

    if "te" in detected_scripts and "kn" in detected_scripts:
        return "kn"

    if "kn" in detected_scripts and "ml" in detected_scripts:
        return "kn"

    if len(detected_scripts) > 1:
        raise MixedLanguageError(
            "Mixed-language documents are not supported. Please provide content in a single supported language."
        )

    return detected_scripts[0]
