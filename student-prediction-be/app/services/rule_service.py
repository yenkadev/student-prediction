"""Hai bộ luật chấm điểm rủi ro đã được chốt từ thực nghiệm."""

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "outputs" / "rules" / "rule_based_config.json"

SOURCE_1_FIELDS = [
    "Curricular units 1st sem (enrolled)",
    "Curricular units 1st sem (approved)",
    "Curricular units 2nd sem (enrolled)",
    "Curricular units 2nd sem (approved)",
    "Curricular units 2nd sem (grade)",
    "Curricular units 2nd sem (without evaluations)",
    "Tuition fees up to date",
    "Debtor",
]
SOURCE_2_FIELDS = [
    "GPA",
    "Attendance_Rate",
    "Stress_Index",
    "Study_Hours_per_Day",
    "Assignment_Delay_Days",
    "Internet_Access",
    "Part_Time_Job",
]
REQUIRED_FIELDS = {
    "student_dropout_and_success": SOURCE_1_FIELDS,
    "student_dropout": SOURCE_2_FIELDS,
}

_config: dict[str, dict[str, Any]] | None = None


def _load_config() -> dict[str, dict[str, Any]]:
    """Đọc cấu hình điểm và ngưỡng đã lựa chọn trên validation set."""
    global _config
    if _config is None:
        if not CONFIG_PATH.exists():
            raise RuntimeError(
                "Không tìm thấy outputs/rules/rule_based_config.json. "
                "Hãy chạy notebook Rule-based Scoring trước."
            )
        with CONFIG_PATH.open(encoding="utf-8") as file:
            _config = json.load(file)
    return _config


def required_fields(data_source: str) -> list[str]:
    """Trả về các trường đầu vào của bộ luật tương ứng."""
    if data_source not in REQUIRED_FIELDS:
        raise ValueError(f"Nguồn dữ liệu không được hỗ trợ: {data_source}")
    return list(REQUIRED_FIELDS[data_source])


def _is_missing(value: Any) -> bool:
    """Nhận diện None và NaN từ dữ liệu JSON, CSV hoặc pandas."""
    return value is None or (isinstance(value, float) and math.isnan(value))


def _read_numeric(fields: Mapping[str, Any], field: str, data_source: str) -> float:
    """Đọc trường số và dùng giá trị điền thiếu được học từ train khi cần."""
    if field not in fields:
        raise ValueError(f"Thiếu trường bắt buộc: {field}")
    value = fields[field]
    if _is_missing(value):
        value = _load_config()[data_source]["imputation_values_from_train"][field]
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} phải là một giá trị số") from error


def _read_yes_no(fields: Mapping[str, Any], field: str, data_source: str) -> str:
    """Đọc trường Yes/No và chuẩn hóa chữ hoa, chữ thường."""
    if field not in fields:
        raise ValueError(f"Thiếu trường bắt buộc: {field}")
    value = fields[field]
    if _is_missing(value):
        value = _load_config()[data_source]["imputation_values_from_train"][field]
    normalized = str(value).strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValueError(f"{field} chỉ chấp nhận 'Yes' hoặc 'No'")
    return normalized


def _score_source_1(fields: Mapping[str, Any]) -> tuple[int, list[str], list[str]]:
    """Chấm điểm dữ liệu học vụ và tài chính của Nguồn 1."""
    source = "student_dropout_and_success"
    enrolled_1 = _read_numeric(fields, "Curricular units 1st sem (enrolled)", source)
    approved_1 = _read_numeric(fields, "Curricular units 1st sem (approved)", source)
    enrolled_2 = _read_numeric(fields, "Curricular units 2nd sem (enrolled)", source)
    approved_2 = _read_numeric(fields, "Curricular units 2nd sem (approved)", source)
    grade_2 = _read_numeric(fields, "Curricular units 2nd sem (grade)", source)
    without_evaluations = _read_numeric(
        fields, "Curricular units 2nd sem (without evaluations)", source
    )
    tuition_up_to_date = _read_numeric(fields, "Tuition fees up to date", source)
    debtor = _read_numeric(fields, "Debtor", source)

    ratio_1 = approved_1 / enrolled_1 if enrolled_1 > 0 else 0.0
    ratio_2 = approved_2 / enrolled_2 if enrolled_2 > 0 else 0.0
    score = 0
    factors: list[str] = []
    recommendations: list[str] = []

    if ratio_2 < 0.50:
        score += 3
        factors.append("Tỷ lệ môn đạt học kỳ 2 dưới 50%")
        recommendations.append("Tư vấn học vụ và lập kế hoạch học lại các môn chưa đạt")
    elif ratio_2 < 0.75:
        score += 1
        factors.append("Tỷ lệ môn đạt học kỳ 2 dưới 75%")
        recommendations.append("Theo dõi tiến độ hoàn thành môn học trong học kỳ tiếp theo")

    if grade_2 < 10:
        score += 2
        factors.append("Điểm trung bình học kỳ 2 dưới 10")
        recommendations.append("Bố trí hỗ trợ học tập cho các môn có kết quả thấp")
    elif grade_2 < 12:
        score += 1
        factors.append("Điểm trung bình học kỳ 2 dưới 12")
        recommendations.append("Theo dõi kết quả học tập trong học kỳ tiếp theo")

    if ratio_1 < 0.50:
        score += 2
        factors.append("Tỷ lệ môn đạt học kỳ 1 dưới 50%")
        recommendations.append("Rà soát các môn nền tảng chưa đạt")
    elif ratio_1 < 0.75:
        score += 1
        factors.append("Tỷ lệ môn đạt học kỳ 1 dưới 75%")
        recommendations.append("Theo dõi việc hoàn thành các môn còn thiếu")

    if tuition_up_to_date == 0:
        score += 2
        factors.append("Học phí chưa được đóng đúng hạn")
        recommendations.append("Liên hệ tư vấn học phí và phương án hỗ trợ tài chính")
    if debtor == 1:
        score += 1
        factors.append("Sinh viên đang có công nợ")
        recommendations.append("Rà soát tình trạng công nợ và kế hoạch thanh toán")
    if without_evaluations >= 2:
        score += 1
        factors.append("Không tham gia đánh giá ít nhất 2 môn ở học kỳ 2")
        recommendations.append("Liên hệ xác minh nguyên nhân không tham gia đánh giá")

    return score, factors, recommendations


def _score_source_2(fields: Mapping[str, Any]) -> tuple[int, list[str], list[str]]:
    """Chấm điểm hành vi và điều kiện học tập của Nguồn 2."""
    source = "student_dropout"
    gpa = _read_numeric(fields, "GPA", source)
    attendance = _read_numeric(fields, "Attendance_Rate", source)
    stress = _read_numeric(fields, "Stress_Index", source)
    study_hours = _read_numeric(fields, "Study_Hours_per_Day", source)
    delay = _read_numeric(fields, "Assignment_Delay_Days", source)
    internet = _read_yes_no(fields, "Internet_Access", source)
    part_time_job = _read_yes_no(fields, "Part_Time_Job", source)

    score = 0
    factors: list[str] = []
    recommendations: list[str] = []
    if gpa < 2.0:
        score += 3
        factors.append("GPA dưới 2.0")
        recommendations.append("Tư vấn học tập và lập kế hoạch cải thiện GPA")
    elif gpa < 2.5:
        score += 1
        factors.append("GPA từ 2.0 đến dưới 2.5")
        recommendations.append("Theo dõi kết quả học tập trong học kỳ tiếp theo")
    if attendance < 75:
        score += 2
        factors.append("Tỷ lệ chuyên cần dưới 75%")
        recommendations.append("Liên hệ sinh viên và xác định nguyên nhân nghỉ học")
    elif attendance < 85:
        score += 1
        factors.append("Tỷ lệ chuyên cần từ 75% đến dưới 85%")
        recommendations.append("Theo dõi chuyên cần và nhắc nhở đi học đầy đủ")
    if stress >= 7:
        score += 2
        factors.append("Mức độ căng thẳng cao")
        recommendations.append("Đề xuất tư vấn tâm lý và theo dõi sức khỏe tinh thần")
    elif stress >= 5:
        score += 1
        factors.append("Mức độ căng thẳng cần theo dõi")
        recommendations.append("Theo dõi mức độ căng thẳng định kỳ")
    if study_hours < 2:
        score += 1
        factors.append("Thời gian tự học dưới 2 giờ mỗi ngày")
        recommendations.append("Hỗ trợ xây dựng thời gian biểu học tập")
    if delay >= 3:
        score += 1
        factors.append("Nộp bài trễ từ 3 ngày trở lên")
        recommendations.append("Nhắc hạn bài và hỗ trợ kỹ năng quản lý thời gian")
    if internet == "no":
        score += 1
        factors.append("Không có điều kiện truy cập Internet")
        recommendations.append("Hỗ trợ thiết bị hoặc địa điểm truy cập Internet")
    if part_time_job == "yes":
        score += 1
        factors.append("Công việc làm thêm có thể ảnh hưởng việc học")
        recommendations.append("Tư vấn cân bằng thời gian làm thêm và học tập")
    return score, factors, recommendations


def predict(features: Mapping[str, Any], data_source: str) -> dict[str, Any]:
    """Chấm điểm một sinh viên và áp dụng ngưỡng đã chốt trên validation set."""
    missing_fields = [field for field in required_fields(data_source) if field not in features]
    if missing_fields:
        raise ValueError(f"Thiếu trường bắt buộc cho {data_source}: {missing_fields}")

    if data_source == "student_dropout_and_success":
        raw_score, factors, recommendations = _score_source_1(features)
    else:
        raw_score, factors, recommendations = _score_source_2(features)

    config = _load_config()[data_source]
    max_score = int(config["max_score"])
    alert_threshold = int(config["alert_threshold_raw"])
    high_threshold = int(config["high_threshold_raw"])
    normalized_score = raw_score / max_score

    if raw_score < alert_threshold:
        risk_level = "low"
    elif raw_score < high_threshold:
        risk_level = "medium"
    else:
        risk_level = "high"

    if not factors:
        factors = ["Không phát hiện yếu tố rủi ro đáng kể"]
        recommendations = ["Tiếp tục theo dõi định kỳ"]

    return {
        "prediction": "Dropout" if raw_score >= alert_threshold else "No Dropout",
        "risk_score": normalized_score,
        "risk_level": risk_level,
        "risk_factors": factors,
        "recommendations": list(dict.fromkeys(recommendations)),
        "score_type": "normalized_rule_score",
    }
