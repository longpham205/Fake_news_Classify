from typing import Dict, List


# ================================
# CONFIG RULE (dễ chỉnh)
# ================================

FAKE_LABELS = {
    "phishing": "Tin giả dạng lừa đảo (Phishing)",
    "deepfake": "Tin giả Deepfake",
    "financial_scam": "Lừa đảo tài chính",
    "hoax": "Tin đồn sai sự thật",
    "malware": "Phát tán mã độc",
}

CONFIDENCE_HIGH = 0.7
CONFIDENCE_MEDIUM = 0.4
CONFIDENCE_LOW = 0.2


def _confidence_level(confidence: float) -> str:
    if confidence >= CONFIDENCE_HIGH:
        return "high"
    if confidence >= CONFIDENCE_MEDIUM:
        return "medium"
    if confidence >= CONFIDENCE_LOW:
        return "low"
    return "unknow"


def _border_class(label: str, confidence: float) -> str:
    if label == "true_news":
        return "Chúc mừng bạn!"
    if confidence > CONFIDENCE_MEDIUM and confidence < CONFIDENCE_HIGH:
        return "Cần kiểm chứng thêm!"
    if confidence < CONFIDENCE_MEDIUM:
        return "Không đủ thông tin"
    return "Xin hãy cẩn thận!"

def _color_class(label: str, confidence: float) -> str:
    if confidence > CONFIDENCE_HIGH:
        if label == "true_news":
            return "text-green"
        return "text-red"
    if confidence > CONFIDENCE_MEDIUM and confidence < CONFIDENCE_HIGH:
        return "text-orange"
    return "text-gray"
    


def _collect_reasons(label: str, explanation: Dict) -> List[str]:
    reasons = []
    
    print("label:", label)

    if label == "true_news":
        reasons.append("Đây là  TIN THẬT với dự đoán có độ tin cậy rất cao\n")

    # suspicious phrases
    suspicious = explanation.get("suspicious_phrases", [])
    if suspicious:
        if label == "true_news":
            reasons.append("Tuy nhiên:\n")
        for item in suspicious:
            reasons.append(
                f"{item.get('note')}: '{item.get('phrase')}'\n"
            )

    # eda analysis
    eda = explanation.get("eda_analysis")
    if eda and eda.get("eda_reasons"):
        if label == "true_news":
            reasons.append("CHÚ Ý:\n")
        for r in eda["eda_reasons"]:
            reasons.append(r)

    # fallback
    if not reasons:
        reasons.append("Không phát hiện dấu hiệu đủ mạnh để kết luận")

    return reasons


# ================================
# MAIN MAPPER
# ================================

def map_result_to_ui(model_output: Dict) -> Dict:
    """
    Mapping model raw output -> UIResponse
    """

    prediction = model_output.get("prediction", {})
    explanation = model_output.get("explanation", {})

    label = prediction.get("label", "unknown")
    confidence = float(prediction.get("confidence", 0.0))
    top_predictions = prediction.get("top_predictions", [])

    # ================================
    # Decide final label
    # ================================

    if model_output.get("status") != "predicted" or confidence < CONFIDENCE_LOW:
        final_label = "uncertain"
        final_label_text = "Chưa thể kết luận"

    elif label == "true_news" and confidence >= CONFIDENCE_HIGH:
        final_label = "true_news"
        final_label_text = "Tin thật"

    elif label in FAKE_LABELS and confidence >= CONFIDENCE_MEDIUM:
        final_label = label
        final_label_text = FAKE_LABELS[label]

    else:
        final_label = "uncertain"
        final_label_text = "Chưa thể kết luận"

    # ================================
    # Build UI response
    # ================================

    ui_response = {
        "status": "success",
        "result": {
            "final_label": final_label,
            "final_label_text": final_label_text,
            "confidence": confidence,
            "confidence_level": _confidence_level(confidence),
            "ui_state": {
                "border_class": _border_class(final_label, confidence),
                "color_class": _color_class(final_label, confidence)
            }
        },
        "top_predictions": top_predictions,
        "reasons": {
            "summary": _collect_reasons(final_label,explanation)
        }
    }

    return ui_response
