"""Rule-based scoring cho nguy cơ sinh viên bỏ học."""

from collections.abc import Mapping
from typing import Any


REQUIRED_FIELDS = (
    "GPA",
    "Attendance_Rate",
    "Stress_Index",
    "Study_Hours_per_Day",
    "Assignment_Delay_Days",
    "Internet_Access",
    "Part_Time_Job",
)


def map_risk_level(score: int) -> str:
    """Chuyển điểm rủi ro thành mức cảnh báo."""
    if score >= 6:
        return "Cao"
    elif score >= 3:
        return "Trung bình"
    else:
        return "Thấp"
    
def read_numeric(student: Mapping[str, Any], field: str) -> float:
    """Đọc và kiểm tra một trường dữ liệu số."""
    if field not in student:
        raise ValueError(f"Thiếu trường bắt buộc: {field}")

    try:
        return float(student[field])
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field} phải là một giá trị số"
        ) from error
    
def read_yes_no(student: Mapping[str, Any], field: str) -> str:
    """Đọc và chuẩn hóa giá trị Yes/No."""
    if field not in student:
        raise ValueError(f"Thiếu trường bắt buộc: {field}")

    value = str(student[field]).strip().lower()

    if value not in {"yes", "no"}:
        raise ValueError(
            f"{field} chỉ chấp nhận 'Yes' hoặc 'No'"
        )

    return value

def calculate_risk(student: Mapping[str, Any]) -> dict[str, Any]:
    """Tính điểm, mức rủi ro, nguyên nhân và khuyến nghị."""
    if not isinstance(student, Mapping):
        raise TypeError("student phải là dictionary")

    gpa = read_numeric(student, "GPA")
    attendance = read_numeric(student, "Attendance_Rate")
    stress = read_numeric(student, "Stress_Index")
    study_hours = read_numeric(student, "Study_Hours_per_Day")
    assignment_delay = read_numeric(
        student,
        "Assignment_Delay_Days"
    )
    internet_access = read_yes_no(student, "Internet_Access")
    part_time_job = read_yes_no(student, "Part_Time_Job")

    score = 0
    reasons = []
    recommendations = []

    # GPA
    if gpa < 2.0:
        score += 3
        reasons.append("GPA dưới 2.0")
        recommendations.append(
            "Tư vấn học tập và lập kế hoạch cải thiện GPA"
        )
    elif gpa < 2.5:
        score += 1
        reasons.append("GPA từ 2.0 đến dưới 2.5")
        recommendations.append(
            "Theo dõi kết quả học tập trong học kỳ tiếp theo"
        )

    # Chuyên cần
    if attendance < 75:
        score += 2
        reasons.append("Tỷ lệ chuyên cần dưới 75%")
        recommendations.append(
            "Liên hệ sinh viên và xác định nguyên nhân nghỉ học"
        )
    elif attendance < 85:
        score += 1
        reasons.append(
            "Tỷ lệ chuyên cần từ 75% đến dưới 85%"
        )
        recommendations.append(
            "Theo dõi chuyên cần và nhắc nhở đi học đầy đủ"
        )

    # Căng thẳng
    if stress >= 7:
        score += 2
        reasons.append("Mức độ căng thẳng cao")
        recommendations.append(
            "Đề xuất tư vấn tâm lý và theo dõi sức khỏe tinh thần"
        )
    elif stress >= 5:
        score += 1
        reasons.append("Mức độ căng thẳng cần theo dõi")
        recommendations.append(
            "Theo dõi mức độ căng thẳng định kỳ"
        )

    # Thời gian tự học
    if study_hours < 2:
        score += 1
        reasons.append("Thời gian tự học dưới 2 giờ mỗi ngày")
        recommendations.append(
            "Hỗ trợ xây dựng thời gian biểu học tập"
        )

    # Nộp bài trễ
    if assignment_delay >= 3:
        score += 1
        reasons.append("Nộp bài trễ từ 3 ngày trở lên")
        recommendations.append(
            "Nhắc hạn bài và hỗ trợ kỹ năng quản lý thời gian"
        )

    # Truy cập Internet
    if internet_access == "no":
        score += 1
        reasons.append("Không có điều kiện truy cập Internet")
        recommendations.append(
            "Hỗ trợ thiết bị hoặc địa điểm truy cập Internet"
        )

    # Công việc làm thêm
    if part_time_job == "yes":
        score += 1
        reasons.append(
            "Công việc làm thêm có thể ảnh hưởng việc học"
        )
        recommendations.append(
            "Tư vấn cân bằng thời gian làm thêm và học tập"
        )

    if not reasons:
        reasons.append(
            "Không phát hiện yếu tố rủi ro đáng kể"
        )
        recommendations.append(
            "Tiếp tục theo dõi định kỳ"
        )

    return {
        "risk_score": score,
        "risk_level": map_risk_level(score),
        "risk_reasons": reasons,
        "recommendations": recommendations
    }