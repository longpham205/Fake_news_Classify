from fastapi import APIRouter, HTTPException
from web.backend.services.feedback_service import FeedbackService # Đảm bảo đúng đường dẫn import

router = APIRouter()
feedback_service = FeedbackService()

@router.post("/feedback")
def save_feedback(feedback: dict):
    """
    Nhận feedback từ frontend và lưu vào file JSON qua FeedbackService
    """
    try:
        # Kiểm tra dữ liệu thô gửi lên (để debug)
        print(f"Nhận feedback: {feedback}")
        
        # Gọi service để lưu vào file JSON
        result = feedback_service.save_feedback(feedback)
        
        return result
    except Exception as e:
        print(f"Lỗi khi lưu feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Không thể lưu đánh giá")