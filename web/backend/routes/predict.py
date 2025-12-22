#routes/predict.py

from fastapi import APIRouter, HTTPException
from web.backend.schemas import NewsInput, UIResponse
from web.backend.services.infer_service import InferService
from web.backend.services.result_mapper import map_result_to_ui

router = APIRouter()

# Khởi tạo service 1 lần
infer_service = InferService()


@router.post(
    "/predict",
    response_model=UIResponse,
    summary="Đánh giá tin tức",
    description="Nhận nội dung tin tức và trả về kết quả phân loại tin giả"
)
def predict(news: NewsInput):
    """
    Controller layer:
    - Nhận dữ liệu từ frontend
    - Gọi infer_service
    - Mapping kết quả sang UI format
    """

    try:
        # 1. Convert Pydantic → dict
        input_data = news.model_dump()

        # 2. Gọi mô hình AI (raw model output)
        raw_model_output = infer_service.run_infer(input_data)

        # 3. Mapping sang UI response (đúng contract frontend)
        ui_response = map_result_to_ui(raw_model_output)
        
        print(ui_response)

        return ui_response

    except Exception as e:
        # Không expose lỗi nội bộ ra frontend
        raise HTTPException(
            status_code=500,
            detail="Internal error during prediction"
        )
