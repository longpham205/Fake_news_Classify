# preprocessing/preprocess/text_cleaner.py

import re
import unicodedata
from configs.config_preprocess import LOWERCASE_MODE, UNICODE_NORMAL_FORM


# Patterns used for controlled lowercase
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
ALL_CAPS_PATTERN = re.compile(r"\b[A-Z]{3,}\b")

HTML_PATTERN = re.compile(r"<.*?>")


def _controlled_lowercase(text: str) -> str:
    """
    Lowercase text while preserving:
    - URLs
    - Emails
    - ALL-CAPS tokens (important phishing / scam cues)
    """

    protected_spans = []

    for pattern in [URL_PATTERN, EMAIL_PATTERN, ALL_CAPS_PATTERN]:
        for m in pattern.finditer(text):
            protected_spans.append((m.start(), m.end()))

    protected_spans = sorted(protected_spans)

    result = []
    last_idx = 0

    for start, end in protected_spans:
        # Lowercase text before protected span
        if last_idx < start:
            result.append(text[last_idx:start].lower())
        # Keep protected span as-is
        result.append(text[start:end])
        last_idx = end

    # Lowercase remaining tail
    if last_idx < len(text):
        result.append(text[last_idx:].lower())

    return "".join(result)


def clean_text(text: str) -> str:
    """
    Clean raw text without introducing synthetic noise.
    """

    # --- Unicode normalization ---
    text = unicodedata.normalize(UNICODE_NORMAL_FORM, text)

    # --- Remove HTML tags ---
    text = HTML_PATTERN.sub(" ", text)

    # --- Controlled lowercase ---
    if LOWERCASE_MODE == "full":
        text = text.lower()
    elif LOWERCASE_MODE == "controlled":
        text = _controlled_lowercase(text)
    # else: "none" → do nothing

    # --- Normalize whitespace ---
    text = re.sub(r"\s+", " ", text).strip()

    return text
