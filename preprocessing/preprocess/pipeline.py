# preprocessing/preprocess/pipeline.py

import pandas as pd

from .validators import validate_dataframe, validate_text
from .text_cleaner import clean_text
from .word_segmenter import segment_vi
from .augmentation import augment_text
from .feature_extractor import extract_aux_features
from configs.config_preprocess import (
    TRAIN_MODE,
    AUGMENTATION_ENABLED_MODES,
    MIN_TOKEN_LENGTH,
    LABEL2ID,
)


def format_phobert_input(text: str) -> str:
    """
    Format text for PhoBERT input.
    """
    return f" {text} "


def preprocess_row(row, mode: str):
    """
    Preprocess a single dataframe row.
    """

    # --- Merge title + text ---
    raw_text = f"{row['title']}. {row['text']}"

    if not validate_text(raw_text):
        return None

    # --- Cleaning ---
    text = clean_text(raw_text)

    # --- Word segmentation ---
    text = segment_vi(text)

    # --- Token-length filter (AFTER segmentation) ---
    token_count = len(text.split())
    if token_count < MIN_TOKEN_LENGTH:
        return None

    # --- Augmentation (TRAIN ONLY) ---
    if mode in AUGMENTATION_ENABLED_MODES:
        text = augment_text(text)

    # --- Extract auxiliary features ---
    features = extract_aux_features(text)

    # --- PhoBERT formatting ---
    text = format_phobert_input(text)

    return {
        "id": row["id"],
        "text": text,
        "label": LABEL2ID[row["label"]],
        **features,
    }


def preprocess_dataframe(df: pd.DataFrame, mode: str = TRAIN_MODE) -> pd.DataFrame:
    """
    Full preprocessing pipeline.
    """

    validate_dataframe(df)

    processed_rows = []

    for _, row in df.iterrows():
        processed = preprocess_row(row, mode)
        if processed is not None:
            processed_rows.append(processed)

    return pd.DataFrame(processed_rows)
