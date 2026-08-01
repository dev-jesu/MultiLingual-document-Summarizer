from __future__ import annotations

import re
from typing import Optional

DEFAULT_LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
}

DEFAULT_LANGUAGE_LABELS = {
    "en": "English",
    "ta": "தமிழ்",
    "hi": "हिंदी",
    "te": "తెలుగు",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "mr": "मराठी",
}


def parse_supported_languages(raw_value: Optional[str] = None) -> dict[str, str]:
    """Parse a comma-separated language list into a supported-language map."""
    if not raw_value:
        return dict(DEFAULT_LANGUAGE_NAMES)

    supported: dict[str, str] = {}
    for code in raw_value.split(","):
        normalized = code.strip().lower()
        if normalized in DEFAULT_LANGUAGE_NAMES:
            supported[normalized] = DEFAULT_LANGUAGE_NAMES[normalized]
    return supported or dict(DEFAULT_LANGUAGE_NAMES)


def normalize_language_code(code: Optional[str], supported_languages: Optional[dict[str, str]] = None) -> Optional[str]:
    """Normalize a language code to a supported short code, if possible."""
    if code is None:
        return None

    normalized = str(code).strip().lower()
    if not normalized or normalized == "auto":
        return None

    aliases = {
        "english": "en",
        "tamil": "ta",
        "hindi": "hi",
        "telugu": "te",
        "kannada": "kn",
        "malayalam": "ml",
        "marathi": "mr",
    }
    if normalized in aliases:
        normalized = aliases[normalized]

    available = set((supported_languages or parse_supported_languages()).keys())
    if normalized in available:
        return normalized
    return None


def get_language_name(code: Optional[str], *, native: bool = False) -> str:
    """Return a human-readable language name for a supported code."""
    normalized = normalize_language_code(code)
    if not normalized:
        return DEFAULT_LANGUAGE_NAMES["en"]
    return DEFAULT_LANGUAGE_LABELS[normalized] if native else DEFAULT_LANGUAGE_NAMES[normalized]


def contains_script(text: str, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(text))
