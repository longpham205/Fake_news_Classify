# infer/eda_loader.py

import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from configs.config_infer import EDA_FILES, MAX_EXPLAIN_PHRASES


class EDAStats:
    """
    Load and compare EDA statistics for post-hoc explanation during inference.
    Explanations are statistical comparisons, NOT causal attributions.
    """

    def __init__(self):
        # -------- Load EDA artifacts from config --------
        self.label_distribution = self._load_csv(EDA_FILES["label_distribution"])
        self.label_numeric_profiles = self._load_json(EDA_FILES["label_numeric_profiles"])
        self.label_binary_stats = self._load_json(EDA_FILES["label_binary_stats"])
        self.label_text_length_stats = self._load_json(EDA_FILES["label_text_length_stats"])
        self.label_time_distribution = self._load_csv(EDA_FILES["label_time_distribution"])

    # =====================================================
    # ----------------- LOADERS ---------------------------
    # =====================================================

    def _load_json(self, path) -> Dict[str, Any]:
        path = Path(path)
        if not path.exists():
            print(f"[Warning] EDA JSON file not found: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_csv(self, path) -> pd.DataFrame:
        path = Path(path)
        if not path.exists():
            print(f"[Warning] EDA CSV file not found: {path}")
            return pd.DataFrame()
        return pd.read_csv(path)

    # =====================================================
    # ----------------- PRIORS ----------------------------
    # =====================================================

    def get_label_prior(self, label: str) -> float:
        """
        Prior probability P(label) from training data distribution.
        Used as weak contextual information, not a decision rule.
        """
        if self.label_distribution.empty:
            return 0.0

        row = self.label_distribution[self.label_distribution["label"] == label]
        if row.empty:
            return 0.0

        return float(row["ratio"].values[0])

    # =====================================================
    # ----------------- TEXT LENGTH -----------------------
    # =====================================================

    def check_text_length(self, label: str, text_length: int) -> List[str]:
        reasons = []
        stats = self.label_text_length_stats.get(label)
        if not stats:
            return reasons
        p10 = stats['text_word_count'].get("p10")
        p90 = stats['text_word_count'].get("p90")

        if p10 is not None and text_length < p10:
            reasons.append(
                "Độ dài văn bản ngắn hơn khoảng phổ biến của nhóm này trong dữ liệu huấn luyện"
            )
        if p90 is not None and text_length > p90:
            reasons.append(
                "Độ dài văn bản dài hơn khoảng phổ biến của nhóm này trong dữ liệu huấn luyện"
            )

        return reasons

    # =====================================================
    # ----------------- NUMERIC FEATURES ------------------
    # =====================================================

    def compare_numeric_features(
        self, label: str, features: Dict[str, float]
    ) -> List[str]:
        reasons = []
        profile = self.label_numeric_profiles.get(label)
        if not profile:
            return reasons
        for feat, value in features.items():
      
            if feat not in profile:
                continue
            if value == -1:
                continue
            mean = profile[feat].get("mean")
            std = profile[feat].get("std")
            
            if mean is None or std is None or std == 0:
                continue
            z = abs(value - mean) / std
            if z > 1.5:
                text = ""
                if feat == "num_shares" :
                    text = "chia sẻ"
                else : text = "bình luận"
                reasons.append(
                    f"Số lượng {text} lệch nhẹ so với phân phối thường thấy của nhóm {label}"
                )

        return reasons

    # =====================================================
    # ----------------- BINARY FEATURES -------------------
    # =====================================================

    def compare_binary_features(
        self, label: str, binary_features: Dict[str, bool]
    ) -> List[str]:
        reasons = []
        stats = self.label_binary_stats.get(label)
        if not stats:
            return reasons

        for feat, present in binary_features.items():
            if not present or feat not in stats:
                continue
            ratio = stats[feat]
            if ratio >= 0.5:
                reasons.append(
                    f"Đặc trưng '{feat}' thường xuất hiện trong nhóm {label} theo dữ liệu huấn luyện"
                )
        return reasons

    # =====================================================
    # ----------------- TIME DISTRIBUTION -----------------
    # =====================================================

    def check_publish_time(self, label: str, hour: int) -> List[str]:
        reasons = []
        if self.label_time_distribution.empty:
            return reasons

        subset = self.label_time_distribution[self.label_time_distribution["label"] == label]
        if subset.empty:
            return reasons

        hour_row = subset[subset["hour"] == hour]
        if hour_row.empty:
            return reasons

        avg_ratio = subset["ratio"].mean()
        hour_ratio = hour_row["ratio"].values[0]

        if hour_ratio > avg_ratio * 1.3:
            reasons.append(
                "Thời điểm đăng bài phù hợp với phân phối thời gian thường thấy của nhóm này"
            )
        return reasons

    # =====================================================
    # ----------------- MAIN EXPLAIN ----------------------
    # =====================================================

    def explain(self, label: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate EDA-based explanation by comparing input features
        with training data distributions.
        """
        reasons: List[str] = []

        reasons += self.compare_numeric_features(label, features.get("numeric", {}))
        reasons += self.compare_binary_features(label, features.get("binary", {}))
        reasons += self.check_text_length(label, features.get("text_length", 0))

        prior = self.get_label_prior(label)

        return {
            "eda_reasons": reasons,
            "num_matches": len(reasons),
            "label_prior": round(prior, 4),
            "eda_confidence": min(len(reasons) / MAX_EXPLAIN_PHRASES, 1.0)
        }