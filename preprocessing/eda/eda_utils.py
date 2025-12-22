# preprocessing/eda/eda_utils.py

import json
import os
from typing import Dict, List, Optional

import pandas as pd
import numpy as np


# =========================
# File & directory helpers
# =========================

def ensure_dir(path: str):
    if path:
        os.makedirs(path, exist_ok=True)


def save_json(obj, path: str):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def save_csv(df: pd.DataFrame, path: str):
    ensure_dir(os.path.dirname(path))
    df.to_csv(path, index=False)


# =========================
# Numeric statistics
# =========================

def numeric_summary(
    series: pd.Series,
    quantiles: Optional[List[float]] = None
) -> Dict:
    """
    Compute robust numeric statistics for EDA.
    - Defensive against dtype issues
    - Quantiles are config-driven
    """
    if series is None:
        return {}

    s = pd.to_numeric(series, errors="coerce").dropna()

    if s.empty:
        return {}

    stats = {
        "count": int(s.count()),
        "mean": float(s.mean()),
        "std": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
    }

    if quantiles:
        for q in quantiles:
            key = f"p{int(q * 100)}"
            stats[key] = float(s.quantile(q))

    return stats


def count_summary(series: pd.Series) -> Dict:
    """
    For long-tail count features (num_shares, num_comments)
    """
    s = pd.to_numeric(series, errors="coerce").dropna()

    if s.empty:
        return {}

    return {
        "count": int(s.count()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()),
        "p75": float(s.quantile(0.75)),
        "p90": float(s.quantile(0.90)),
        "max": float(s.max()),
    }


# =========================
# Binary statistics
# =========================

def binary_summary(series: pd.Series) -> Dict:
    """
    Binary EDA statistics:
    - true_ratio
    - false_ratio
    - count
    """
    if series is None:
        return {}

    s = series.dropna()
    if s.empty:
        return {}

    # normalize values to {0,1}
    s = s.astype(int)

    total = len(s)
    true_count = int(s.sum())
    false_count = total - true_count

    return {
        "count": total,
        "true_ratio": true_count / total,
        "false_ratio": false_count / total,
    }


# =========================
# Categorical statistics
# =========================

def categorical_summary(
    series: pd.Series,
    top_k: int = 10,
    normalize: bool = True
) -> Dict:
    """
    Stable categorical distribution for EDA.
    """
    s = series.dropna().astype(str)

    if s.empty:
        return {}

    vc = s.value_counts()

    if normalize:
        vc = vc / vc.sum()

    vc = vc.head(top_k)

    return {k: float(v) for k, v in vc.items()}


# =========================
# Time utilities
# =========================

def parse_datetime(
    series: pd.Series,
    date_format: Optional[str] = None
) -> pd.Series:
    """
    Safe datetime parsing for EDA
    """
    return pd.to_datetime(series, format=date_format, errors="coerce")
