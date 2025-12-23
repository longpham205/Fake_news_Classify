# preprocessing/preprocess/augmentation.py

import json
import random
import re
from configs.config_preprocess import (
    SENTENCE_SHUFFLE_PROB,
    SYNONYM_PROB,
    SYNONYM_MAP_PATH
)

# Synonym map must be label-safe
def load_synonyms(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

SYNONYM_MAP = load_synonyms(SYNONYM_MAP_PATH)


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
