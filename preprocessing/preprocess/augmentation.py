# preprocessing/augmentation.py

import random
import re
from configs.config_preprocessing import (
    SENTENCE_SHUFFLE_PROB,
    SYNONYM_PROB,
)

# Synonym map must be label-safe
SYNONYM_MAP = {
    "xác_minh": ["verify", "validate", "xác_thực"],
    "tài_khoản": ["account", "acc"],
}


def shuffle_sentences(text: str) -> str:
    """
    Shuffle sentence order to reduce position bias.
    Applied only when sentence count is sufficient.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) < 4:
        return text

    random.shuffle(sentences)
    return " ".join(sentences)


def apply_synonym_noise(text: str) -> str:
    """
    Replace at most ONE synonym per type to avoid semantic drift.
    """
    for word, syns in SYNONYM_MAP.items():
        if word in text and random.random() < SYNONYM_PROB:
            text = text.replace(word, random.choice(syns), 1)
    return text


def augment_text(text: str) -> str:
    """
    Apply synthetic augmentation.
    TRAIN MODE ONLY – must be guarded by pipeline.
    """
    if random.random() < SENTENCE_SHUFFLE_PROB:
        text = shuffle_sentences(text)

    text = apply_synonym_noise(text)
    return text
