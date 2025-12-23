# preprocessing/eda/eda_config.py
"""
EDA configuration file

Purpose:
- Define feature groups for statistical profiling
- Ensure stable, interpretable, and reusable EDA outputs
- NO model / training / inference logic here
"""

from configs.shared import LABEL_ORDER, LABELS

# =========================
# Label configuration
# =========================

LABEL_FIELD = "label"


# =========================
# Feature groups
# =========================

# --- Numeric features (continuous) ---
NUMERIC_FEATURES = [
    "readability_score",
    "clickbait_score",
    "trust_score",
    "plagiarism_score",
    "source_reputation",
]

# --- Text length related numeric features ---
TEXT_LENGTH_FEATURES = [
    "word_count",
    "char_count",
]

# --- Count-based numeric features ---
COUNT_FEATURES = [
    "num_shares",
    "num_comments",
]

# --- Binary features ---
BINARY_FEATURES = [
    "has_images",
    "has_videos",
    "is_satirical",
]

# --- Categorical features ---
CATEGORICAL_FEATURES = [
    "source",
    "category",
    "political_bias",
    "fact_check_rating",
]


# =========================
# Text fields (EDA only)
# =========================

TEXT_FIELDS = [
    "title",
    "summary",
    "text",
]


# =========================
# Time / date configuration
# =========================

DATE_FIELD = "date_published"

# allowed: "year", "month"
TIME_GRAIN = "month"

# None = infer automatically
DATE_FORMAT = None


# =========================
# Columns excluded from EDA
# =========================

EXCLUDED_COLUMNS = [
    "id",
    "url",
    "author",
    LABEL_FIELD,
    DATE_FIELD,
]


# =========================
# Quantiles
# =========================

QUANTILES = [0.1, 0.25, 0.5, 0.75, 0.9]
