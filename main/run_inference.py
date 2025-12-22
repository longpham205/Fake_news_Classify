# run_infer.py
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
from src.infer.infer import NewsInferencer

if __name__ == "__main__":
    inferencer = NewsInferencer()

    sample_input = {
        "title": "Thanh toán gần đây của bạn cho Spotify Premium không thành công",
        "author": "Nguyễn Văn A",
        "text": (
            "Bộ phận kỹ thuật xác nhận sự cố đã được khắc phục hoàn toàn. Tài khoản của khách hàng vừa được đăng nhập từ một thiết bị chưa từng sử dụng trước đây. Thông báo này nhằm giúp khách hàng kiểm soát an toàn tài khoản. Nếu không phải do khách hàng thực hiện, vui lòng liên hệ kênh hỗ trợ chính thức để được hướng dẫn khóa phiên đăng nhập và thay đổi thông tin bảo mật."
        ),
        "source": "email",
        "date_published": "2025-12-19",  
        "url": "http://khoahocchungkhoanmienphi.com",
        "fact_check_rating": None,
        "has_images": False,
        "has_videos": False,
        "num_shares": -1,
        "num_comments": -1,
    }

    result = inferencer.infer(sample_input)

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
