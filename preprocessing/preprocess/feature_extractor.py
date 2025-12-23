# preprocessing/preprocess/feature_extractor.py
from configs.config_preprocess import PANIC_WORDS_PATH
import json
from pathlib import Path

def load_panic_words(file_path: str) -> set:
    path = Path(file_path)
    if not path.exists():
        print(f"[Warning] PANIC_WORDS JSON file not found: {file_path}")
        return set()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return set(data.get("panic_words", []))

PANIC_WORDS = load_panic_words(PANIC_WORDS_PATH)


def extract_aux_features(text: str) -> dict:
    """
    Extract auxiliary features for analysis or fusion models.
    These features MUST NOT be used to directly alter text.
    """

    tokens = text.split()
    token_count = len(tokens)

    panic_count = sum(1 for t in tokens if t in PANIC_WORDS)

    return {
        "token_count": token_count,
        "char_count": len(text),
        "panic_word_count": panic_count,
        "panic_density": panic_count / max(token_count, 1),
    }
