# infer/phrase_extractor.py

import re
from typing import List, Dict

# ---------------- keyword groups ----------------
SUSPICIOUS_KEYWORDS = {
    "financial_scam": [
        "chuyển khoản",
        "trúng thưởng",
        "hoàn tiền",
        "đầu tư",
        "lợi nhuận cao",
    ],
    "phishing": [
        "xác minh tài khoản",
        "cập nhật thông tin",
        "khóa tài khoản",
        "click",
        "đường link",
    ],
    "hoax": [
        "khẩn cấp",
        "ngay lập tức",
        "chia sẻ ngay",
    ],
    "malware": [
        "tải file",
        "cài đặt ứng dụng",
        "file đính kèm",
    ],
    "deepfake": [
        "ảnh giả",
        "video giả",
    ],
}

REGEX_PATTERNS = {
    "url": r"http[s]?://\S+",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b\d{9,11}\b",
}

MAX_PHRASES = 5


def extract_suspicious_phrases(
    segmented_text: str,
    predicted_label: str
) -> List[Dict[str, str]]:
    """
    Extract suspicious phrases based on predicted label and regex patterns.
    """

    text = segmented_text.lower()
    results: List[Dict[str, str]] = []
    seen_phrases = set()

    # ---------------- label-specific keywords ----------------
    keywords = SUSPICIOUS_KEYWORDS.get(predicted_label, [])
    for kw in keywords:
        if kw in text and kw not in seen_phrases:
            results.append({
                "phrase": kw,
                "type": "keyword",
                "strength": "medium",
                "note": f"Cụm từ thường gặp trong nhóm {predicted_label}"
            })
            seen_phrases.add(kw)

        if len(results) >= MAX_PHRASES:
            return results

    # ---------------- regex patterns ----------------
    for ptype, pattern in REGEX_PATTERNS.items():
        matches = re.findall(pattern, segmented_text)
        for m in set(matches):
            if m in seen_phrases:
                continue

            results.append({
                "phrase": m,
                "type": ptype,
                "strength": "weak",
                "note": f"Phát hiện mẫu {ptype} trong văn bản"
            })
            seen_phrases.add(m)

            if len(results) >= MAX_PHRASES:
                return results

    return results
