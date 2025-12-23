# preprocessing/eda/run_eda.py

import argparse
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)
import pandas as pd

# Ensure module import works when running as script

from preprocessing.eda.eda_utils import save_json, save_csv
from preprocessing.eda.eda_stats import (
    compute_data_quality,
    compute_label_distribution,
    compute_numeric_stats,
    compute_binary_stats,
    compute_categorical_stats,
    compute_text_length_stats,
    compute_temporal_stats,
)
from configs.config_eda import LABEL_FIELD, DATE_FIELD


# =========================================================
# Main EDA runner
# =========================================================

def run_eda(input_csv: str):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"[EDA] Input file not found: {input_csv}")
    
    output_dir =os.path.join(os.path.abspath(os.path.join(os.path.dirname(input_csv),"../..")), "dataset/data_eda")

    os.makedirs(output_dir, exist_ok=True)

    print(f"[EDA] Loading data from: {input_csv}")
    df = pd.read_csv(input_csv)

    print(f"[EDA] Loaded shape: {df.shape}")
    print(f"[EDA] Columns: {list(df.columns)}")

    # --- basic schema validation ---
    if LABEL_FIELD not in df.columns:
        raise ValueError(f"[EDA] Missing required column: {LABEL_FIELD}")

    if DATE_FIELD not in df.columns:
        print(f"[EDA][WARN] DATE_FIELD '{DATE_FIELD}' not found. Temporal stats will be skipped.")

    # =====================================================
    # Data quality
    # =====================================================
    print("[EDA] Computing data quality...")
    quality = compute_data_quality(df)
    save_json(quality, os.path.join(output_dir, "data_quality.json"))

    # =====================================================
    # Label distribution
    # =====================================================
    print("[EDA] Computing label distribution...")
    label_dist = compute_label_distribution(df)
    save_csv(label_dist, os.path.join(output_dir, "label_distribution.csv"))

    # =====================================================
    # Numeric stats
    # =====================================================
    print("[EDA] Computing numeric statistics...")
    global_num, label_num = compute_numeric_stats(df)
    save_json(global_num, os.path.join(output_dir, "global_numeric_stats.json"))
    save_json(label_num, os.path.join(output_dir, "label_numeric_profiles.json"))

    # =====================================================
    # Binary stats
    # =====================================================
    print("[EDA] Computing binary statistics...")
    binary_stats = compute_binary_stats(df)
    save_json(binary_stats, os.path.join(output_dir, "label_binary_stats.json"))

    # =====================================================
    # Categorical stats
    # =====================================================
    print("[EDA] Computing categorical statistics...")
    categorical_stats = compute_categorical_stats(df)
    save_json(categorical_stats, os.path.join(output_dir, "label_categorical_stats.json"))

    # =====================================================
    # Text length stats
    # =====================================================
    print("[EDA] Computing text length statistics...")
    text_len_stats = compute_text_length_stats(df)
    save_json(text_len_stats, os.path.join(output_dir, "label_text_length_stats.json"))

    # =====================================================
    # Temporal stats
    # =====================================================
    print("[EDA] Computing temporal statistics...")
    temporal_df = compute_temporal_stats(df)
    if temporal_df is not None and not temporal_df.empty:
        save_csv(
            temporal_df,
            os.path.join(output_dir, "label_time_distribution.csv")
        )
    else:
        print("[EDA][INFO] No temporal statistics generated.")

    print("[EDA] DONE ✔ All artifacts saved to:", output_dir)


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EDA statistics pipeline")
    parser.add_argument(
        "--input",
        default=os.path.join(root_dir,"dataset/data_raw/vietnamese_news_dataset.csv"),
        help="Path to input CSV (data_raw.csv)"
    )

    args = parser.parse_args()
    run_eda(args.input)
