# src/train/config.py
"""
Training configuration

Purpose:
- Hyperparameters for fine-tuning PhoBERT
- Device & reproducibility
"""

import os
import torch
from configs.shared import (
    MODEL_NAME,
    NUM_CLASSES,
    MAX_SEQ_LENGTH,
    RANDOM_SEED,
    ROOT_DIR
)

# =========================
# Paths
# =========================

DATA_DIR = os.path.join(ROOT_DIR, "dataset", "data_processed")
OUTPUT_DIR = os.path.join(ROOT_DIR, "checkpoints")


# =========================
# Model (imported from shared)
# =========================

# MODEL_NAME
# NUM_CLASSES
# MAX_SEQ_LENGTH


# =========================
# Regularization
# =========================

DROPOUT_RATE = 0.2


# =========================
# Training hyperparameters
# =========================

BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5
WEIGHT_DECAY = 0.01


# =========================
# Reproducibility
# =========================

# RANDOM_SEED


# =========================
# Device
# =========================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
