# Giao diện cảnh báo nguy cơ bỏ học

Ứng dụng React + TypeScript + Vite cho phép giảng viên chọn nguồn dữ liệu, chọn giải pháp đánh giá và xem kết quả cảnh báo.

## Chức năng chính

- Chọn `student_dropout_and_success.csv` hoặc `student_dropout.csv`.
- Chọn Machine Learning hoặc Rule-based Scoring.
- Upload CSV/XLSX để đánh giá nhiều sinh viên qua API thật.
- Hiển thị dự đoán, điểm/mức rủi ro, yếu tố ảnh hưởng và khuyến nghị.
- Xuất kết quả đánh giá hàng loạt ra CSV.
- Lưu batch gần nhất trong trình duyệt để không mất kết quả khi reload.
- Mở chi tiết sinh viên của batch đồng bộ mà không cần MongoDB.
- Hỗ trợ bố cục desktop và mobile.
- Hỗ trợ hội thoại khi backend đã cấu hình MongoDB và Gemini.

## Cài đặt và chạy

Khởi động backend tại `http://localhost:8000`, sau đó mở terminal khác:

```powershell
cd student-prediction-fe
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Mở `http://127.0.0.1:5173`.

## Kiểm tra chất lượng

```powershell
npm run lint
npm run build
```

Frontend sử dụng `src/api/httpClient.ts` để gọi backend thật. `mockClient.ts` chỉ được giữ lại làm dữ liệu minh họa/phát triển, không phải client mặc định của ứng dụng.

## Cấu trúc chính

- `src/api/`: kiểu dữ liệu và HTTP client.
- `src/components/NewAssessment.tsx`: chọn nguồn dữ liệu và giải pháp.
- `src/components/UploadPanel.tsx`: upload file và gọi `/predict/batch/sync`.
- `src/components/ChatPanel.tsx`: hội thoại và hiển thị kết quả cá nhân.
- `src/components/BatchResults.tsx`: bảng kết quả và xuất CSV.
