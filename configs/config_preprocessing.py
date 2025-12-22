# preprocessing/preprcess/config.py

"""
Preprocessing configuration

Purpose:
- Text normalization & cleaning
- Data augmentation (TRAIN ONLY)
- No model / label definition here
"""

# =========================
# Modes
# =========================

TRAIN_MODE = "train"
INFER_MODE = "infer"

AUGMENTATION_ENABLED_MODES = {TRAIN_MODE}


# =========================
# Randomness (delegated to shared seed)
# =========================

from configs.shared import (
    RANDOM_SEED,
    LABELS,
    LABEL2ID
    )


# =========================
# Cleaning & Normalization
# =========================

# Lowercase strategy:
# - "none"
# - "full"
# - "controlled" (recommended for security NLP)
LOWERCASE_MODE = "controlled"

# Unicode normalization form
UNICODE_NORMAL_FORM = "NFKC"

# Minimum token length (after segmentation)
MIN_TOKEN_LENGTH = 20


# =========================
# Augmentation (TRAIN ONLY)
# =========================

# Replace token with noise
TOKEN_REPLACE_PROB = 0.3

# Shuffle sentence order
SENTENCE_SHUFFLE_PROB = 0.2

# Inject synonym noise
SYNONYM_PROB = 0.15


# =========================
# Synthetic data controls
# =========================

MAX_FILLER_TOKENS = 2

# Protect URLs, emails, IPs, hashes
PROTECT_CRITICAL_TOKENS = True
