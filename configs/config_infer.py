# src/infer/config.py

"""
Inference configuration

Purpose:
- Runtime inference behaviour
- Confidence & explainability policy
"""

import sys
from pathlib import Path
import torch

from configs.shared import (
    MODEL_NAME,
    NUM_CLASSES,
    MAX_SEQ_LENGTH,
    LABEL2ID,
    ID2LABEL,
    LABEL_DESCRIPTIONS,
)

# =========================================================
# Paths
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

CHECKPOINT_PATH = ROOT_DIR / "checkpoints" / "phobert_best.pt"


# =========================================================
# Device
# =========================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# =========================================================
# Inference policy
# =========================================================

# Confidence thresholds
CONFIDENCE_HIGH = 0.7
CONFIDENCE_MEDIUM = 0.4

# Top-k predictions
RETURN_TOP_K = 3


# =========================================================
# Explainability
# =========================================================

ENABLE_EXPLAIN = True
MAX_EXPLAIN_PHRASES = 5


# =========================================================
# EDA comparison (optional)
# =========================================================

ENABLE_EDA_COMPARE = True

EDA_DIR = ROOT_DIR / "dataset" / "data_eda"

EDA_FILES = {
    "data_quality": EDA_DIR / "data_quality.json",
    "global_numeric_stats": EDA_DIR / "global_numeric_stats.json",
    "label_binary_stats": EDA_DIR / "label_binary_stats.json",
    "label_categorical_stats": EDA_DIR / "label_categorical_stats.json",
    "label_distribution": EDA_DIR / "label_distribution.csv",
    "label_numeric_profiles": EDA_DIR / "label_numeric_profiles.json",
    "label_text_length_stats": EDA_DIR / "label_text_length_stats.json",
    "label_time_distribution": EDA_DIR / "label_time_distribution.csv",
}
