# Hệ thống cảnh báo sớm nguy cơ sinh viên bỏ học

Đồ án môn **Hỗ trợ đưa ra quyết định dựa trên dữ liệu**.

Hệ thống phân tích dữ liệu học tập để dự đoán nguy cơ bỏ học, giải thích nguyên nhân và đề xuất biện pháp hỗ trợ phù hợp.

## Mục tiêu

Hệ thống cung cấp:

- Kết quả dự đoán tình trạng học tập.
- Điểm và mức rủi ro: Thấp, Trung bình, Cao.
- Các yếu tố làm tăng nguy cơ.
- Khuyến nghị hỗ trợ cho từng sinh viên.

## Dữ liệu

### Dataset 1: Student Dropout and Academic Success

- File: `data/student_dropout_and_success.csv`
- Quy mô: 4.424 dòng, 35 cột.
- Target: `Dropout`, `Enrolled`, `Graduate`.
- Được đánh giá độc lập bằng ML Classification và Rule-based Scoring.

### Dataset 2: Student Dropout Prediction

- File: `data/student_dropout.csv`
- Quy mô: 10.000 dòng, 19 cột.
- Target: `Dropout`, gồm `0` và `1`.
- Có missing values ở một số thuộc tính.
- Được đánh giá độc lập bằng ML Classification và Rule-based Scoring.
- Đây là dữ liệu mô phỏng, vì vậy kết quả cần được kiểm chứng lại trên dữ liệu thực tế trước khi triển khai.

Hai dataset không có khóa sinh viên chung nên không được nối theo từng dòng. Kết quả của chúng được kết hợp tại tầng hỗ trợ ra quyết định.

## Cấu trúc repository

```text
app/        Web application layer (React + TypeScript + Vite)
data/       Dữ liệu đầu vào
docs/       Báo cáo và slide
notebooks/  EDA, ML Classification, XAI và Rule-based Scoring
outputs/    Dữ liệu đã chia, mô hình, dự đoán và kết quả đánh giá
src/        Code dùng lại cho backend
tests/      Kiểm thử tự động cho các chức năng dùng chung
```

## Notebook

```text
notebooks/01_eda.ipynb
notebooks/02_prepare_data.ipynb
notebooks/02_ml_classification_xai.ipynb
notebooks/03_rule_based_scoring.ipynb
notebooks/04_solution_comparison.ipynb
```

## Cài đặt

Yêu cầu Python 3.10 trở lên.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Mở notebook bằng VS Code hoặc Jupyter, chọn Python kernel trong `.venv`, sau đó chạy các ô theo thứ tự từ trên xuống.

## Chạy hệ thống tích hợp

Các notebook phải được chạy trước để tạo model, cấu hình luật và các file trong `outputs/`.

Khởi động backend:

```powershell
cd student-prediction-be
$env:PYTHONPATH='.'
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Mở terminal khác và khởi động frontend:

```powershell
cd student-prediction-fe
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Truy cập `http://127.0.0.1:5173`. Tại màn hình đánh giá mới, chọn đúng file nguồn và giải pháp trước khi upload dữ liệu.

Hệ thống hỗ trợ đủ bốn tổ hợp:

1. `student_dropout_and_success.csv` + Machine Learning.
2. `student_dropout_and_success.csv` + Rule-based Scoring.
3. `student_dropout.csv` + Machine Learning.
4. `student_dropout.csv` + Rule-based Scoring.

Hai nguồn không được merge theo từng dòng. Điểm Rule-based là điểm luật đã chuẩn hóa, không phải xác suất thống kê; giao diện hiển thị rõ loại điểm để tránh diễn giải sai.

## Rule-based Scoring

Các yếu tố đang được sử dụng:

- GPA.
- Attendance Rate.
- Stress Index.
- Study Hours per Day.
- Assignment Delay Days.
- Internet Access.
- Part-time Job.

Kết quả phân tầng trên Dataset 2:

| Mức rủi ro | Số sinh viên | Tỷ lệ dropout |
|---|---:|---:|
| Thấp | 3.127 | 5,63% |
| Trung bình | 4.295 | 20,35% |
| Cao | 2.578 | 50,58% |

Các file kết quả:

```text
outputs/risk_rules_table.csv
outputs/student_risk_scored.csv
outputs/sample_decision_outputs.csv
```

### Sử dụng trong backend

Backend có thể gọi trực tiếp hàm chấm điểm:

```python
from src import calculate_risk

student = {
    "GPA": 2.3,
    "Attendance_Rate": 80,
    "Stress_Index": 5,
    "Study_Hours_per_Day": 3,
    "Assignment_Delay_Days": 0,
    "Internet_Access": "Yes",
    "Part_Time_Job": "No",
}

result = calculate_risk(student)
```

Kết quả gồm:

- `risk_score`: tổng điểm rủi ro.
- `risk_level`: `Thấp`, `Trung bình` hoặc `Cao`.
- `risk_reasons`: danh sách nguyên nhân.
- `recommendations`: danh sách khuyến nghị.

Chạy kiểm thử tự động:

```powershell
python -m unittest discover -s tests -v
```

## Phân công

| Thành viên | Phụ trách |
|---|---|
| Quý | ML Classification và XAI |
| Yến | Rule-based Scoring |
| Tùng | Backend, AI Pipeline và LLM |
| Lâm | Web Application |
| Quân | Review báo cáo |

## Lưu ý

- Không commit thư mục `.venv`.
- Không chỉnh trực tiếp notebook của thành viên khác khi chưa thống nhất.
- Chạy lại toàn bộ notebook trước khi commit.
- Rule-based Scoring là hệ thống cảnh báo, không khẳng định chắc chắn sinh viên sẽ bỏ học.
