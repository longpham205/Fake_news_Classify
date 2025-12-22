import json
import os
from datetime import datetime

class FeedbackService:
    def __init__(self, base_path="result/feedback"):
        self.base_path = base_path
        # Đảm bảo thư mục cha result/feedback luôn tồn tại
        os.makedirs(self.base_path, exist_ok=True)

    def save_feedback(self, full_data: dict):
        """
        Lưu feedback gộp vào file theo ngày:
        result/feedback/YYYY_MM_DD.json
        """
        # 1. Tạo tên file dựa trên ngày hiện tại
        date_str = datetime.now().strftime("%Y_%m_%d")
        file_path = os.path.join(self.base_path, f"{date_str}.json")

        # 2. Đọc dữ liệu cũ nếu file đã tồn tại
        data_list = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data_list = json.load(f)
                    if not isinstance(data_list, list):
                        data_list = []
            except (json.JSONDecodeError, Exception):
                data_list = []

        # 3. Thêm feedback mới vào danh sách
        # Bạn có thể thêm timestamp lúc lưu để dễ tra cứu sau này
        full_data["saved_at"] = datetime.now().strftime("%H:%M:%S")
        data_list.append(full_data)

        # 4. Ghi lại vào file (Gộp theo ngày)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "file": f"{date_str}.json",
                "message": f"Đã lưu feedback vào file ngày {date_str}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }