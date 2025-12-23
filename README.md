# 📰 Fake News Detection with PhoBERT (Vietnamese)

## 📌 Giới thiệu dự án

Dự án **Fake News Detection** nhằm xây dựng một hệ thống phát hiện tin giả tiếng Việt dựa trên mô hình **PhoBERT**.
Hệ thống bao gồm **toàn bộ pipeline AI hoàn chỉnh**, từ xử lý dữ liệu đến triển khai web:

* Phân tích dữ liệu (EDA)
* Tiền xử lý văn bản
* Huấn luyện mô hình học sâu
* Suy luận & giải thích kết quả
* Triển khai Web App với FastAPI + Frontend

Ứng dụng cho phép người dùng **nhập nội dung tin tức** và nhận kết quả:

* Nhãn dự đoán (tin thật / tin giả / lừa đảo, …)
* Độ tin cậy (confidence score)
* Giải thích dựa trên thống kê dữ liệu & các cụm từ nghi ngờ

---

## 🧠 Kiến trúc tổng thể

```
Dataset
   ↓
EDA (Exploratory Data Analysis)
   ↓
Preprocessing (Clean – Segment – Feature)
   ↓
Training (PhoBERT)
   ↓
Inference + Explainability
   ↓
Web Application (FastAPI + UI)
```

---

## 📂 Cấu trúc thư mục chính

```
Fake_news_Classify/
├── dataset/            # Dữ liệu raw, processed và EDA
├── preprocessing/      # EDA & pipeline tiền xử lý
├── json/               # Các dữ liệu cho hệ thống
├── src/
│   ├── model/          # Định nghĩa mô hình PhoBERT
│   ├── train/          # Huấn luyện & đánh giá
│   ├── infer/          # Suy luận & giải thích
├── web/                # Backend FastAPI + Frontend
├── main/               # Các file chạy pipeline
├── checkpoints/        # Model đã huấn luyện
├── result/             # Kết quả training & feedback
└── README.md
```

---

## ⚙️ Cài đặt môi trường

### 1️⃣ Clone repository

```bash
git clone https://github.com/your-username/Fake_news_Classify.git
cd Fake_news_Classify
```

---

### 2️⃣ Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 3️⃣ Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt
```

---

4️⃣ Tải dữ liệu

Bạn cần tải dataset tiếng Việt lưu vào thư mục chuẩn trong project:
Tải từ link :
```bash
https://drive.google.com/file/d/1a6zlJf8OvfXme_G_Rg6BVcLMEC98XGVK/view?usp=drive_link
```

Lưu tại:
```bash
data/
```

---

5️⃣ Tải checkpoint mô hình (nếu cần)

Nếu bạn muốn chạy thử inference hoặc tiếp tục huấn luyện mà không train từ đầu, bạn cần checkpoint tốt nhất:

Tải từ link :
```bash
https://drive.google.com/file/d/1ekFoDWUUCNksQbwCTs3o0oKKfci6wPap/view?usp=sharing
```

Lưu tại:
```bash
checkpoints/phobert_best.pt
```

---

## CÁC BƯỚC CHẠY NHANH
Chạy huấn luện nhanh bằng :
```bash
python main/run_training.py
```

Khởi động hệ thống web (Backend + Frontend):

```bash
python main/run_web.py
```

---

## CÁC BƯỚC CHẠY CHI TIẾT
## 📊 Chạy phân tích dữ liệu (EDA)

Thực hiện thống kê & phân tích dữ liệu đầu vào:

```bash
python preprocessing/eda/run_eda.py
```

📌 **Kết quả EDA được lưu tại**:

```
dataset/data_eda/
├── data_quality.json
├── label_distribution.csv
├── label_text_length_stats.json
└── ...
```

---

## 🧹 Tiền xử lý dữ liệu

Chạy pipeline tiền xử lý văn bản (làm sạch, tách từ, chia tập dữ liệu):

```bash
python main/run_preprocessing.py
```

📌 **Dữ liệu sau xử lý được lưu tại**:

```
dataset/data_processed/
├── train.csv
├── val.csv
├── test.csv
└── train_processed.csv
```

---

## 🏋️ Huấn luyện mô hình

Huấn luyện mô hình PhoBERT trên dữ liệu đã xử lý:

```bash
python main/run_training.py
```

📌 **Kết quả huấn luyện**:

* Model tốt nhất:

```
checkpoints/phobert_best.pt
```

* Lịch sử huấn luyện:

```
result/training_history.csv
```

---

## 🔍 Suy luận (Inference)

Chạy thử suy luận với văn bản bất kỳ:

```bash
python main/run_inference.py
```

📌 Kết quả suy luận bao gồm:

* Nhãn dự đoán
* Xác suất
* Giải thích dựa trên EDA & cụm từ nghi ngờ

---

## 🌐 Chạy Web Application

Khởi động hệ thống web (Backend + Frontend):

```bash
python main/run_web.py
```

Sau đó mở trình duyệt và truy cập:

```
http://127.0.0.1:5500 (cho live server)
```

---

## 🧾 API chính

### `POST /predict`

* Nhận nội dung tin tức
* Trả về kết quả dự đoán và giải thích

### `POST /feedback`

* Nhận phản hồi người dùng
* Lưu phục vụ cải thiện mô hình trong tương lai

📌 **Feedback được lưu tại**:

```
result/feedback/YYYY_MM_DD.json
```

---

## 📈 Nơi lưu kết quả

| Thành phần          | Vị trí                        |
| ------------------- | ----------------------------- |
| Model đã huấn luyện | `checkpoints/`                |
| Kết quả EDA         | `dataset/data_eda/`           |
| Dữ liệu đã xử lý    | `dataset/data_processed/`     |
| Lịch sử training    | `result/training_history.csv` |
| Feedback người dùng | `result/feedback/`            |

---

## 🚀 Công nghệ sử dụng

* **PhoBERT** (Transformer cho tiếng Việt)
* **PyTorch**
* **FastAPI**
* **Pandas / NumPy**
* **HTML / CSS / JavaScript**

---

## 📌 Hướng phát triển

* Tích hợp thêm nhiều mô hình phân loại
* Huấn luyện lại mô hình từ feedback người dùng
* Mở rộng sang các thể loại tin tức khác
* Triển khai Docker / Cloud

---

## LINK TÀI LIỆU CHI TIẾT
```bash
https://docs.google.com/document/d/1skVWtzMcxeqqmsnvNoLLbbAzw2284bzrZVnz55b3DOg/edit?usp=sharing
```

---

## 👨‍💻 Tác giả

**Long Pham**
Project phục vụ học tập & nghiên cứu AI / NLP
