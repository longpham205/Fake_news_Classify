#configs/shared.py

"""
Shared configuration for the Fake News Detection system

Purpose:
- Single source of truth for labels, model identity, and input constraints
- Used consistently across:
  preprocessing / EDA / training / inference / backend
- Prevent silent mismatches between train and inference
"""

# =========================================================
# Project metadata
# =========================================================

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# =========================================================
# Project metadata
# =========================================================

PROJECT_NAME = "Fake News Detection"
PROJECT_VERSION = "1.0.0"


# =========================================================
# Labels (GLOBAL & IMMUTABLE)
# =========================================================

LABELS = [
    "true_news",
    "deepfake",
    "financial_scam",
    "hoax",
    "malware",
    "phishing",
]

# Stable label ordering (DO NOT CHANGE after training)
LABEL_ORDER = LABELS.copy()

# Mapping
LABEL2ID = {label: idx for idx, label in enumerate(LABEL_ORDER)}
ID2LABEL = {idx: label for label, idx in LABEL2ID.items()}

NUM_CLASSES = len(LABEL_ORDER)


# =========================================================
# Label semantics (for UI / explainability)
# =========================================================

LABEL_DESCRIPTIONS = {
    "true_news": "Tin tức chính thống, không có dấu hiệu lừa đảo hoặc sai lệch",
    "deepfake": "Tin giả được tạo hoặc chỉnh sửa bằng công nghệ AI",
    "financial_scam": "Tin lừa đảo liên quan đến tiền bạc hoặc giao dịch tài chính",
    "hoax": "Tin bịa đặt hoặc gây hiểu lầm, không có cơ sở xác thực",
    "malware": "Tin chứa hoặc dẫn tới mã độc gây hại cho thiết bị",
    "phishing": "Tin nhằm đánh cắp thông tin cá nhân như mật khẩu, OTP, tài khoản",
}


# =========================================================
# Model identity (SHARED BETWEEN TRAIN & INFER)
# =========================================================

# Pretrained backbone
MODEL_NAME = "vinai/phobert-base"

# Maximum sequence length used for:
# - tokenization
# - training
# - inference
MAX_SEQ_LENGTH = 256


# =========================================================
# Reproducibility
# =========================================================

# Global random seed
RANDOM_SEED = 42


# =========================================================
# Safety checks (optional, but recommended)
# =========================================================

def assert_label_consistency():
    """
    Ensure label mappings are internally consistent.
    Call this once at startup if needed.
    """
    assert len(LABEL2ID) == NUM_CLASSES
    assert len(ID2LABEL) == NUM_CLASSES

    for label, idx in LABEL2ID.items():
        assert ID2LABEL[idx] == label


def assert_model_config(max_len: int):
    """
    Ensure runtime max length matches shared configuration.
    """
    assert max_len == MAX_SEQ_LENGTH, (
        f"MAX_SEQ_LENGTH mismatch: shared={MAX_SEQ_LENGTH}, runtime={max_len}"
    )
