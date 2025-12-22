#backend/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# ======================================================
# 1. INPUT SCHEMA (Frontend -> Backend)
# ======================================================

class NewsInput(BaseModel):
    title: Optional[str] = Field(None, description="Tiêu đề bài viết")
    author: Optional[str] = Field(None, description="Tác giả")
    text: str = Field(..., description="Nội dung chính")
    source: Optional[str] = Field(None, description="Nguồn tin (email, web, social...)")
    date_published: Optional[date] = Field(None, description="Ngày xuất bản")
    url: Optional[str] = Field(None, description="Đường dẫn bài viết")

    has_images: bool = Field(False, description="Có hình ảnh hay không")
    has_videos: bool = Field(False, description="Có video hay không")
    num_shares: int = Field(0, ge=-1, description="Số lượt chia sẻ")
    num_comments: int = Field(0, ge=-1, description="Số lượt bình luận")


# ======================================================
# 2. MODEL RAW OUTPUT (Internal – KHÔNG gửi frontend)
# ======================================================

class TopPrediction(BaseModel):
    label: str
    probability: float


class ModelPrediction(BaseModel):
    label: str
    confidence: float
    confidence_level: str
    top_predictions: List[TopPrediction]


class SuspiciousPhrase(BaseModel):
    phrase: str
    type: str
    strength: str
    note: Optional[str] = None


class EDAAnalysis(BaseModel):
    eda_reasons: List[str]
    num_matches: int
    label_prior: float
    eda_confidence: float


class ModelExplanation(BaseModel):
    suspicious_phrases: List[SuspiciousPhrase]
    eda_analysis: Optional[EDAAnalysis] = None


class ModelOutput(BaseModel):
    status: str
    prediction: ModelPrediction
    explanation: ModelExplanation


# ======================================================
# 3. UI RESPONSE (Backend -> Frontend)
# ======================================================

class UIState(BaseModel):
    border_class: str
    color_class: str


class FinalResult(BaseModel):
    final_label: str
    final_label_text: str
    confidence: float
    confidence_level: str
    ui_state: UIState


class Reasons(BaseModel):
    summary: List[str]


class UIResponse(BaseModel):
    status: str
    result: FinalResult
    top_predictions: List[TopPrediction]
    reasons: Reasons


# ======================================================
# 4. FEEDBACK SCHEMA (Optional – nếu lưu DB)
# ======================================================

class UserFeedback(BaseModel):
    score: int = Field(..., ge=1, le=5)
    score_text: Optional[str] = None
    comment: Optional[str] = None


class FeedbackRequest(BaseModel):
    feedback_id: str
    evaluation_id: str
    created_at: str

    news_input: NewsInput
    model_output: UIResponse
    user_feedback: UserFeedback
