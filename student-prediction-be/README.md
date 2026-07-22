# Backend cảnh báo nguy cơ bỏ học

FastAPI backend phục vụ hai nguồn dữ liệu và hai giải pháp của đồ án:

| Nguồn dữ liệu | Machine Learning | Rule-based Scoring |
|---|---:|---:|
| `student_dropout_and_success` | Có | Có |
| `student_dropout` | Có | Có |

Hai nguồn được xử lý độc lập, không merge theo sinh viên. Model và cấu hình luật được đọc từ thư mục `../outputs/` đã tạo bởi các notebook thí nghiệm.

## Cài đặt

Từ thư mục gốc của repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r student-prediction-be\requirements.txt
```

## Chạy API

```powershell
cd student-prediction-be
$env:PYTHONPATH='.'
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Kiểm tra tại `http://localhost:8000/health` hoặc tài liệu Swagger tại `http://localhost:8000/docs`.

## API không cần dịch vụ ngoài

### Dự đoán một sinh viên

`POST /predict/single`

```json
{
  "dataSource": "student_dropout",
  "predictionType": "ml",
  "features": {
    "GPA": 2.3,
    "Attendance_Rate": 70,
    "Stress_Index": 8,
    "Study_Hours_per_Day": 2,
    "Assignment_Delay_Days": 4,
    "Internet_Access": "Yes",
    "Part_Time_Job": "No"
  }
}
```

### Dự đoán từ file CSV/XLSX

`POST /predict/batch/sync`

```powershell
curl.exe -X POST http://localhost:8000/predict/batch/sync `
  -F "file=@../outputs/splits/student_dropout_test.csv" `
  -F "dataSource=student_dropout" `
  -F "predictionType=rule_based"
```

API trả kết quả ngay và không cần MongoDB. File phải chứa đủ các feature tương ứng với nguồn dữ liệu đã chọn. Có thể chọn `ml` hoặc `rule_based`.

## Chức năng cần MongoDB hoặc Gemini

- `POST /predict/chat`: cần MongoDB để lưu hội thoại và `GEMINI_API_KEY` để trích xuất thông tin từ văn bản tự nhiên.
- `POST /predict/batch`: phiên bản xử lý nền, cần MongoDB để lưu trạng thái job.
- `POST /predict/batch/sync` và `POST /predict/single`: không cần MongoDB hoặc Gemini.

Sao chép `.env.example` thành `.env` nếu sử dụng chat hoặc batch nền:

```env
GEMINI_API_KEY=your_key
MONGODB_URL=mongodb://localhost:27017
```

## Kiểm thử

Từ thư mục `student-prediction-be`:

```powershell
$env:PYTHONPATH='.'
..\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

Bộ kiểm thử xác nhận cả bốn tổ hợp nguồn dữ liệu × giải pháp, upload đồng bộ và trường hợp thiếu feature.
