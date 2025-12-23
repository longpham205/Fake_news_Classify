# run_infer.py
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, root_dir)
print(root_dir)
from src.infer.infer import NewsInferencer

if __name__ == "__main__":
    inferencer = NewsInferencer()

    sample_input = {
        "title": "Thanh toán gần đây của bạn cho Spotify Premium không thành công",
        "author": "Nguyễn Văn A",
        "text": (
            "Tài khoản của bạn đang bị hạn chế, vui lòng xác minh tại https://security-check-vn.com/update. Google đã chặn một nỗ lực đăng nhập vào tài khoản của bạn. Vui lòng kiểm tra hoạt động thiết bị và đổi mật khẩu ngay tại: http://google-account-recovery-center.net."
        ),
        "source": "email",
        "date_published": "2025-12-19",  
        "url": "http://khoahocchungkhoanmienphi.com",
        "fact_check_rating": None,
        "has_images": False,
        "has_videos": False,
        "num_shares": 10000000,
        "num_comments": 10000,
    }

    result = inferencer.infer(sample_input)

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
