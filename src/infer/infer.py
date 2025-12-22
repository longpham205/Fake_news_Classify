# infer/infer.py
import os
import sys
from typing import Dict, Any, List

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

from src.model.model import PhoBERTClassifier
from configs.config_infer import (
    MODEL_NAME,
    CHECKPOINT_PATH,
    NUM_CLASSES,
    DEVICE,
    MAX_SEQ_LENGTH,
    ID2LABEL,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    RETURN_TOP_K,
    ENABLE_EXPLAIN,
)
from src.infer.phrase_extractor import extract_suspicious_phrases
from src.infer.eda_loader import EDAStats

# ------------------- PATH -------------------
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)


class NewsInferencer:
    """
    End-to-end inference with uncertainty handling and post-hoc explanation.
    """

    def __init__(self):
        # -------- tokenizer --------
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        # -------- model --------
        self.model = PhoBERTClassifier(
            model_name=MODEL_NAME,
            num_classes=NUM_CLASSES
        )
        self.model.load_state_dict(
            torch.load(CHECKPOINT_PATH, map_location=DEVICE)
        )
        self.model.to(DEVICE)
        self.model.eval()

        # -------- EDA --------
        self.eda = EDAStats()

    # =====================================================
    # ----------------- AUX FEATURE COMPUTE --------------
    # =====================================================
    def _compute_aux_features(self, input_json: Dict[str, Any], segmented_text: str) -> Dict[str, Any]:
        """
        Tạo numeric + binary feature để EDA sử dụng
        """
        text = input_json.get("text", "")
        features = {}

        # ---------------- numeric ----------------
        features["numeric"] = {
            "text_word_count": len(text.split()),
            "text_char_count": len(text),
            "num_shares": input_json.get("num_shares", 0),
            "num_comments": input_json.get("num_comments", 0),
        }

        # ---------------- binary ----------------
        features["binary"] = {
            "has_url": bool(input_json.get("url")),
            "has_images": bool(input_json.get("has_images", False)),
            "has_videos": bool(input_json.get("has_videos", False)),
            "has_fact_check": input_json.get("fact_check_rating") is not None,
        }

        # ---------------- text length ----------------
        features["text_length"] = len(text.split())

        return features

    # =====================================================
    # ----------------- PREPROCESS ------------------------
    # =====================================================
    def _preprocess_text(self, title: str, text: str):
        raw_text = f"{title}. {text}".strip()

        # -------- clean & segment --------
        from preprocessing.preprocess.text_cleaner import clean_text
        from preprocessing.preprocess.word_segmenter import segment_vi
        from preprocessing.preprocess.pipeline import format_phobert_input

        cleaned = clean_text(raw_text)
        segmented = segment_vi(cleaned)

        phobert_text = format_phobert_input(segmented)

        return phobert_text, segmented

    # =====================================================
    # ----------------- INFER -----------------------------
    # =====================================================
    def infer(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform inference on a single news item with uncertainty awareness.
        """

        title = input_json.get("title", "")
        text = input_json.get("text")
        if not text:
            raise ValueError("Input must contain 'text' field")

        phobert_text, segmented_text = self._preprocess_text(title, text)
        aux_features = self._compute_aux_features(input_json, segmented_text)

        # -------- tokenize --------
        encoded = self.tokenizer(
            phobert_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_SEQ_LENGTH,
        )
        encoded = {k: v.to(DEVICE) for k, v in encoded.items()}

        # -------- model inference --------
        with torch.no_grad():
            logits = self.model(
                input_ids=encoded["input_ids"],
                attention_mask=encoded["attention_mask"],
            )
            probs = F.softmax(logits, dim=-1).squeeze(0)

        # -------- top-k predictions --------
        top_probs, top_ids = torch.topk(probs, k=min(RETURN_TOP_K, len(probs)))
        top_predictions: List[Dict[str, float]] = [
            {"label": ID2LABEL[int(idx)], "probability": float(prob)}
            for prob, idx in zip(top_probs, top_ids)
        ]

        best_prob = float(top_probs[0])
        best_label = ID2LABEL[int(top_ids[0])]

        # -------- confidence handling --------
        if best_prob >= CONFIDENCE_HIGH:
            confidence_level = "high"
            status = "predicted"
        elif best_prob >= CONFIDENCE_MEDIUM:
            confidence_level = "medium"
            status = "predicted_with_warning"
        else:
            confidence_level = "low"
            status = "uncertain"

        # -------- explanations (only if confident enough) --------
        explanation = {}
        if ENABLE_EXPLAIN and status != "uncertain":
            explanation["suspicious_phrases"] = extract_suspicious_phrases(
                text, best_label
            )
            explanation["eda_analysis"] = self.eda.explain(
                label=best_label,
                features=aux_features
            )

        return {
            "status": status,
            "prediction": {
                "label": best_label if status != "uncertain" else None,
                "confidence": best_prob,
                "confidence_level": confidence_level,
                "top_predictions": top_predictions,
            },
            "explanation": explanation,
        }
