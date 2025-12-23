# preprocessing/eda/eda_stats.py

from collections import defaultdict
import pandas as pd

from configs.config_eda import (
    LABELS,
    LABEL_ORDER,
    LABEL_FIELD,
    NUMERIC_FEATURES,
    TEXT_LENGTH_FEATURES,
    COUNT_FEATURES,
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    TEXT_FIELDS,
    DATE_FIELD,
    TIME_GRAIN,
    DATE_FORMAT,
    QUANTILES,
)

from .eda_utils import (
    numeric_summary,
    count_summary,
    binary_summary,
    categorical_summary,
    parse_datetime,
)


# =========================================================
# (1) DATA QUALITY
# =========================================================

def compute_data_quality(df: pd.DataFrame) -> dict:
    quality = {
        "num_rows": int(len(df)),
        "num_columns": int(df.shape[1]),
        "missing_ratio": {},
        "duplicate_ratio": {},
    }

    for col in df.columns:
        quality["missing_ratio"][col] = float(df[col].isna().mean())

    if "text" in df.columns:
        quality["duplicate_ratio"]["text"] = float(
            df.duplicated(subset=["text"]).mean()
        )

    if "url" in df.columns:
        quality["duplicate_ratio"]["url"] = float(
            df.duplicated(subset=["url"]).mean()
        )

    return quality


# =========================================================
# (2) LABEL DISTRIBUTION
# =========================================================

def compute_label_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[LABEL_FIELD].value_counts().reindex(LABEL_ORDER, fill_value=0)
    ratios = counts / counts.sum()

    return pd.DataFrame({
        "label": counts.index,
        "count": counts.values,
        "ratio": ratios.values,
    })


# =========================================================
# (3) GLOBAL + LABEL-WISE NUMERIC STATS
# =========================================================

def compute_numeric_stats(df: pd.DataFrame):
    global_stats = {}
    label_profiles = defaultdict(dict)

    # --- continuous numeric features ---
    for feat in NUMERIC_FEATURES:
        if feat not in df.columns:
            continue

        global_stats[feat] = numeric_summary(df[feat], QUANTILES)

        for label in LABEL_ORDER:
            sub = df[df[LABEL_FIELD] == label]
            label_profiles[label][feat] = numeric_summary(sub[feat], QUANTILES)

    # --- count / long-tail features ---
    for feat in COUNT_FEATURES:
        if feat not in df.columns:
            continue

        global_stats[feat] = count_summary(df[feat])

        for label in LABEL_ORDER:
            sub = df[df[LABEL_FIELD] == label]
            label_profiles[label][feat] = count_summary(sub[feat])

    return global_stats, label_profiles


# =========================================================
# (4) BINARY STATS
# =========================================================

def compute_binary_stats(df: pd.DataFrame) -> dict:
    results = defaultdict(dict)

    for label in LABEL_ORDER:
        sub = df[df[LABEL_FIELD] == label]

        for feat in BINARY_FEATURES:
            if feat not in df.columns:
                continue

            results[label][feat] = binary_summary(sub[feat])

    return results


# =========================================================
# (5) CATEGORICAL STATS
# =========================================================

def compute_categorical_stats(df: pd.DataFrame, top_k: int = 10) -> dict:
    results = defaultdict(dict)

    for label in LABEL_ORDER:
        sub = df[df[LABEL_FIELD] == label]

        for feat in CATEGORICAL_FEATURES:
            if feat not in df.columns:
                continue

            results[label][feat] = categorical_summary(
                sub[feat],
                top_k=top_k,
                normalize=True
            )

    return results


# =========================================================
# (6) TEXT LENGTH STATS (NON-MUTATING)
# =========================================================

def compute_text_length_stats(df: pd.DataFrame) -> dict:
    results = defaultdict(dict)

    for field in TEXT_FIELDS:
        if field not in df.columns:
            continue

        lengths = df[field].fillna("").astype(str).apply(
            lambda x: len(x.split())
        )

        for label in LABEL_ORDER:
            sub_lengths = lengths[df[LABEL_FIELD] == label]
            results[label][f"{field}_word_count"] = numeric_summary(
                sub_lengths,
                QUANTILES
            )

    return results


# =========================================================
# (7) TEMPORAL STATS
# =========================================================

def compute_temporal_stats(df: pd.DataFrame) -> pd.DataFrame:
    if DATE_FIELD not in df.columns:
        return pd.DataFrame()

    dt = parse_datetime(df[DATE_FIELD], DATE_FORMAT)

    if TIME_GRAIN == "year":
        time_key = dt.dt.year
    elif TIME_GRAIN == "month":
        time_key = dt.dt.to_period("M").astype(str)
    else:
        raise ValueError(f"Unsupported TIME_GRAIN: {TIME_GRAIN}")

    temp_df = (
        pd.DataFrame({
            "time": time_key,
            LABEL_FIELD: df[LABEL_FIELD]
        })
        .dropna()
        .groupby(["time", LABEL_FIELD])
        .size()
        .reset_index(name="count")
        .sort_values("time")
    )

    return temp_df
