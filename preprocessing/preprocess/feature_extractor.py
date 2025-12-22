# preprocessing/feature_extractor.py

PANIC_WORDS = {
    "khẩn_cấp",
    "gấp",
    "ngay_lập_tức",
    "cảnh_báo",
    "nguy_hiểm",
    "đe_doạ",
}


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
