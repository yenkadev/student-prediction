# Thí nghiệm

## 1. Thông tin chung

- Đề tài: Hệ thống cảnh báo sớm nguy cơ sinh viên bỏ học.
- Mục tiêu: So sánh Machine Learning Classification và Rule-based Risk Scoring trên hai nguồn dữ liệu giáo dục khác nhau.
- Phiên bản: 1.0.

Tài liệu này là quy ước chung cho các phần EDA, Machine Learning, Rule-based Scoring, backend, frontend, báo cáo và slide. Mọi thay đổi về target, cách chia dữ liệu, metric hoặc output phải được nhóm thống nhất và cập nhật tại đây trước khi chạy lại thí nghiệm.

## 2. Nguồn dữ liệu

### 2.1. Nguồn 1: `student_dropout_and_success.csv`

- Đường dẫn: `data/student_dropout_and_success.csv`.
- Quy mô: 4.424 dòng, 35 cột.
- Target gốc: `Dropout`, `Enrolled`, `Graduate`.
- Góc nhìn dữ liệu: tuyển sinh, nhân khẩu học, tài chính, học phí và kết quả học kỳ.
- Vai trò: đánh giá nguy cơ bỏ học từ dữ liệu học vụ và hành chính.

### 2.2. Nguồn 2: `student_dropout.csv`

- Đường dẫn: `data/student_dropout.csv`.
- Quy mô: 10.000 dòng, 19 cột.
- Target gốc: `Dropout`, gồm `0` và `1`.
- Góc nhìn dữ liệu: GPA, chuyên cần, thời gian học, stress, nộp bài, điều kiện truy cập Internet và việc làm thêm.
- Vai trò: đánh giá nguy cơ bỏ học từ hành vi và điều kiện học tập.
- Lưu ý: Đây là dữ liệu mô phỏng; kết quả cần được kiểm chứng lại bằng dữ liệu thực tế trước khi triển khai.

## 3. Nguyên tắc sử dụng hai nguồn

- Không merge hai file theo từng dòng hoặc theo sinh viên.
- Hai nguồn không có khóa sinh viên chung và không mô tả cùng một tập người học.
- Mỗi nguồn được làm sạch, chia dữ liệu, huấn luyện và đánh giá độc lập.
- Kết quả chỉ được tổng hợp tại tầng so sánh và hỗ trợ ra quyết định.
- Không so sánh trực tiếp một giải pháp trên Nguồn 1 với một giải pháp khác trên Nguồn 2 để kết luận giải pháp nào tốt hơn.
- Chỉ so sánh trực tiếp ML và Rule-based khi chúng được đánh giá trên cùng test set của cùng một nguồn.

## 4. Chuẩn hóa target

### 4.1. Nguồn 1

Thí nghiệm nhị phân chính sử dụng:

| Target gốc | Target nhị phân | Cách xử lý |
|---|---:|---|
| `Dropout` | `1` | Giữ lại |
| `Graduate` | `0` | Giữ lại |
| `Enrolled` | Không áp dụng | Tạm loại khỏi thí nghiệm nhị phân chính |

Lý do loại `Enrolled`: Đây là trạng thái trung gian, chưa thể khẳng định sinh viên sẽ tốt nghiệp hoặc bỏ học.

Việc loại `Enrolled` chỉ áp dụng cho thí nghiệm nhị phân chính. Nhóm có thể thực hiện thêm thí nghiệm ba lớp nếu còn thời gian, nhưng phải báo cáo riêng và không trộn metric với thí nghiệm nhị phân.

### 4.2. Nguồn 2

Giữ nguyên target:

| Target gốc | Ý nghĩa |
|---:|---|
| `0` | No Dropout |
| `1` | Dropout |

## 5. Chia dữ liệu

Mỗi nguồn được chia độc lập theo tỷ lệ:

- Train: 70%.
- Validation: 15%.
- Test: 15%.
- `random_state = 42`.
- Sử dụng stratified split theo target.

Danh sách dòng thuộc từng tập phải được tạo một lần và lưu lại:

```text
outputs/splits/student_dropout_and_success_split.csv
outputs/splits/student_dropout_split.csv
```

Định dạng tối thiểu:

```csv
row_id,split
0,train
1,test
2,validation
```

ML và Rule-based bắt buộc phải đọc cùng file split. Không được tự chia dữ liệu riêng trong từng notebook.

## 6. Ngăn ngừa rò rỉ dữ liệu

- Chỉ dùng train set để phân tích, chọn feature và xây luật ban đầu.
- Dùng validation set để chọn siêu tham số ML và ngưỡng cảnh báo.
- Chỉ dùng test set một lần để báo cáo kết quả cuối cùng.
- Không thay đổi luật, trọng số, ngưỡng hoặc siêu tham số dựa trên kết quả test set.
- Các bước xử lý như imputation, scaling và encoding phải được fit trên train set rồi áp dụng cho validation/test set.

## 7. Ma trận thí nghiệm

Nhóm thực hiện bốn thí nghiệm chính:

| Mã | Nguồn dữ liệu | Giải pháp |
|---|---|---|
| E1 | `student_dropout_and_success.csv` | Machine Learning Classification |
| E2 | `student_dropout_and_success.csv` | Rule-based Risk Scoring |
| E3 | `student_dropout.csv` | Machine Learning Classification |
| E4 | `student_dropout.csv` | Rule-based Risk Scoring |

Trong mỗi nguồn, hai giải pháp phải sử dụng cùng test set và cùng định nghĩa target.

## 8. Tiêu chí đánh giá

### 8.1. Tiêu chí định lượng

Các metric bắt buộc:

- Precision của lớp Dropout.
- Recall của lớp Dropout.
- F1-score của lớp Dropout.
- F2-score của lớp Dropout.
- Accuracy.
- Confusion matrix.

Nếu giải pháp cung cấp xác suất hoặc điểm liên tục, báo cáo thêm:

- ROC-AUC.
- PR-AUC.

Thứ tự ưu tiên khi lựa chọn giải pháp:

1. Recall Dropout.
2. F2-score.
3. PR-AUC nếu có.
4. F1-score.
5. Accuracy.

Recall và F2 được ưu tiên vì mục tiêu của hệ thống cảnh báo sớm là hạn chế bỏ sót sinh viên có nguy cơ bỏ học.

### 8.2. Tiêu chí định tính

- Khả năng giải thích.
- Chi phí huấn luyện.
- Tốc độ dự đoán.
- Mức phụ thuộc vào dữ liệu.
- Khả năng cập nhật và bảo trì.
- Mức độ thuận tiện khi triển khai thực tế.

## 9. Quy ước cho Machine Learning

- Mỗi nguồn có pipeline và model riêng.
- Logistic Regression có thể được sử dụng làm baseline.
- LightGBM được sử dụng làm mô hình nâng cao nếu phù hợp.
- Xác suất Dropout phải lấy từ `predict_proba`, không lấy từ nhãn `predict`.
- Giải thích mô hình bằng SHAP hoặc phương pháp tương đương.
- Model cuối cùng chỉ được lựa chọn dựa trên validation set.

## 10. Quy ước cho Rule-based Scoring

- Mỗi nguồn có một bộ luật riêng vì feature khác nhau.
- Ngưỡng và trọng số phải có căn cứ từ EDA trên train set hoặc từ tài liệu nghiên cứu được trích dẫn.
- Ngưỡng cảnh báo được kiểm tra trên validation set.
- Kết quả cuối cùng được đánh giá trên cùng test set với ML.
- Rule-based phải trả về điểm, mức rủi ro, nguyên nhân và khuyến nghị.

## 11. Output thống nhất

ML và Rule-based phải được chuẩn hóa về cùng contract:

```json
{
  "data_source": "student_dropout",
  "solution_type": "rule_based",
  "prediction": "Dropout",
  "risk_score": 0.75,
  "risk_level": "high",
  "risk_factors": [],
  "recommendations": []
}
```

Quy ước:

- `data_source`: `student_dropout_and_success` hoặc `student_dropout`.
- `solution_type`: `ml` hoặc `rule_based`.
- `prediction`: `Dropout` hoặc `No Dropout`.
- `risk_score`: giá trị trong khoảng `0.0` đến `1.0` dùng để xếp hạng rủi ro.
- `risk_level`: `low`, `medium` hoặc `high`.
- `risk_factors`: danh sách yếu tố ảnh hưởng.
- `recommendations`: danh sách biện pháp can thiệp.

Với Rule-based, nếu điểm gốc không nằm trong khoảng `0.0` đến `1.0`, phải chuẩn hóa theo điểm tối đa của bộ luật và ghi rõ công thức. Giá trị chuẩn hóa này không được gọi là xác suất thống kê.

## 12. File kết quả bắt buộc

```text
outputs/
├── splits/
│   ├── student_dropout_and_success_split.csv
│   └── student_dropout_split.csv
├── predictions/
│   ├── student_dropout_and_success_ml.csv
│   ├── student_dropout_and_success_rule_based.csv
│   ├── student_dropout_ml.csv
│   └── student_dropout_rule_based.csv
└── solution_comparison.csv
```

Mỗi file dự đoán phải có tối thiểu:

```csv
row_id,y_true,prediction_score,y_pred
```

File `solution_comparison.csv` phải có tối thiểu:

```csv
data_source,solution_type,precision,recall,f1,f2,accuracy
```

## 13. Nguyên tắc kết luận

- Không kết luận ML tốt hơn Rule-based hoặc ngược lại trước khi có kết quả test.
- Kết luận định lượng được đưa ra riêng cho từng nguồn.
- Phần tổng hợp chỉ đánh giá xu hướng và tính ổn định của hai giải pháp qua hai nguồn.
- Có thể đề xuất ML làm bộ dự đoán chính và Rule-based làm lớp giải thích/fallback nếu kết quả thực nghiệm hỗ trợ lựa chọn đó.
- Báo cáo phải trình bày cả ưu điểm, hạn chế và rủi ro khi sử dụng dữ liệu mô phỏng.

## 14. Điều kiện hoàn thành

- [x] Hai nguồn dữ liệu được xử lý độc lập.
- [ ] Cách xử lý `Enrolled` được nhóm xác nhận.
- [x] Hai file split cố định đã được tạo.
- [x] Có hai pipeline ML riêng.
- [x] Có hai bộ Rule-based riêng.
- [x] ML và Rule-based sử dụng cùng test set trong từng nguồn.
- [x] Có đủ bốn file dự đoán.
- [x] Có bảng so sánh định lượng và định tính.
- [x] Có kết luận dựa trên kết quả test.
- [x] Backend và frontend sử dụng output contract thống nhất.
- [ ] README, báo cáo và slide khớp với source và output thực tế.

## 15. Các điểm cần nhóm xác nhận

- [ ] Đồng ý loại `Enrolled` khỏi thí nghiệm nhị phân chính.
- [ ] Đồng ý tỷ lệ Train/Validation/Test là 70/15/15.
- [ ] Đồng ý sử dụng `random_state = 42`.
- [ ] Đồng ý ưu tiên Recall Dropout và F2-score.
- [ ] Đồng ý cấu trúc output và danh sách file kết quả.

Sau khi tất cả điểm trên được xác nhận, cập nhật trạng thái tài liệu từ `Bản đề xuất chờ nhóm xác nhận` thành `Đã được nhóm thống nhất`.
