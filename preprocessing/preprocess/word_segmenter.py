# preprocessing/word_segmenter.py

import re
from pyvi import ViTokenizer


# Regex patterns for critical tokens that must not be segmented
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
HASH_PATTERN = re.compile(r"\b[a-fA-F0-9]{32,64}\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

CRITICAL_PATTERNS = [
    URL_PATTERN,
    EMAIL_PATTERN,
    HASH_PATTERN,
    IP_PATTERN,
]


def _protect_critical_tokens(text: str):
    """
    Replace critical tokens with tokenizer-safe placeholders.
    """
    protected = {}
    idx = 0

    for pattern in CRITICAL_PATTERNS:
        for m in pattern.finditer(text):
            placeholder = f"§§CRIT{idx}§§"
            protected[placeholder] = m.group()
            text = text.replace(m.group(), placeholder)
            idx += 1

    return text, protected


def _restore_critical_tokens(text: str, protected: dict):
    for placeholder, value in protected.items():
        text = text.replace(placeholder, value)
    return text


def segment_vi(text: str) -> str:
    """
    Vietnamese word segmentation compatible with PhoBERT.
    """

    # --- Protect critical tokens ---
    text, protected = _protect_critical_tokens(text)

    # --- Word segmentation ---
    text = ViTokenizer.tokenize(text)

    # --- Restore critical tokens ---
    text = _restore_critical_tokens(text, protected)

    # --- Normalize whitespace ---
    text = re.sub(r"\s+", " ", text).strip()

    return text
