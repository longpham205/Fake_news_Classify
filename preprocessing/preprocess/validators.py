# preprocessing/preprocess/validators.py

from configs.config_preprocess import LABELS


REQUIRED_COLUMNS = [
    "id",
    "title",
    "text",
    "source",
    "date_published",
    "label",
]


def validate_dataframe(df):
    """
    Validate raw dataframe schema and critical null values.
    This function should be called BEFORE any text preprocessing.
    """

    # --- Schema check ---
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # --- Null checks ---
    if df["text"].isnull().any():
        raise ValueError("Null values found in text column")

    if df["label"].isnull().any():
        raise ValueError("Null values found in label column")

    # --- Label legality (vectorized) ---
    invalid_labels = set(df["label"].unique()) - set(LABELS)
    if invalid_labels:
        raise ValueError(f"Invalid labels found: {invalid_labels}")


def validate_text(text):
    """
    Lightweight sanity check for raw text.
    Length-based filtering MUST be done after word segmentation.
    """
    if not isinstance(text, str):
        return False

    if not text.strip():
        return False

    return True
