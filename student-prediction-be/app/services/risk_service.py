"""Điều phối hai nguồn dữ liệu và hai loại giải pháp dự đoán."""

from typing import Any

from app.services import ml_service, rule_service


DATA_SOURCES = ("student_dropout_and_success", "student_dropout")
PREDICTION_TYPES = ("ml", "rule_based")


def validate_selection(data_source: str, prediction_type: str) -> None:
    """Kiểm tra cặp nguồn dữ liệu và giải pháp do client gửi lên."""
    if data_source not in DATA_SOURCES:
        raise ValueError(
            f"dataSource phải là một trong các giá trị: {list(DATA_SOURCES)}"
        )
    if prediction_type not in PREDICTION_TYPES:
        raise ValueError(
            f"predictionType phải là một trong các giá trị: {list(PREDICTION_TYPES)}"
        )


def required_fields(data_source: str, prediction_type: str) -> list[str]:
    """Trả về schema đầu vào của đúng cặp nguồn và giải pháp."""
    validate_selection(data_source, prediction_type)
    if prediction_type == "ml":
        return ml_service.required_fields(data_source)
    return rule_service.required_fields(data_source)


def assess(
    fields: dict[str, Any], prediction_type: str, data_source: str
) -> dict[str, Any]:
    """Đánh giá rủi ro và trả về contract chuẩn cùng trường tương thích cũ."""
    validate_selection(data_source, prediction_type)
    if prediction_type == "ml":
        result = ml_service.predict(fields, data_source)
    else:
        result = rule_service.predict(fields, data_source)

    recommendations = result["recommendations"]
    factors = result["risk_factors"]
    score = round(float(result["risk_score"]), 6)
    prediction = result["prediction"]

    return {
        # Các trường chuẩn dùng cho tích hợp mới.
        "dataSource": data_source,
        "solutionType": prediction_type,
        "prediction": prediction,
        "riskScore": score,
        "riskLevel": result["risk_level"],
        "riskFactors": factors,
        "recommendations": recommendations,
        "scoreType": result["score_type"],
        # Các trường tương thích với giao diện và dữ liệu phiên bản cũ.
        "statusLabel": prediction,
        "riskProb": score,
        "factors": factors,
        "recommendation": "; ".join(recommendations),
    }
