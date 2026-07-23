"""Dự đoán bằng các pipeline Machine Learning đã được chốt trong thực nghiệm."""

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "outputs" / "models"
METADATA_PATH = MODEL_DIR / "ml_model_metadata.json"

_metadata: dict[str, dict[str, Any]] | None = None
_models: dict[str, Any] = {}


def _load_metadata() -> dict[str, dict[str, Any]]:
    """Đọc metadata một lần và lưu trong bộ nhớ của tiến trình backend."""
    global _metadata
    if _metadata is None:
        if not METADATA_PATH.exists():
            raise RuntimeError(
                "Không tìm thấy outputs/models/ml_model_metadata.json. "
                "Hãy chạy notebook Machine Learning trước."
            )
        with METADATA_PATH.open(encoding="utf-8") as file:
            _metadata = json.load(file)
    return _metadata


def supported_data_sources() -> tuple[str, ...]:
    """Trả về hai nguồn dữ liệu có mô hình đã được huấn luyện."""
    return tuple(_load_metadata().keys())


def required_fields(data_source: str) -> list[str]:
    """Trả về đúng thứ tự đặc trưng mà pipeline của một nguồn yêu cầu."""
    metadata = _load_metadata()
    if data_source not in metadata:
        raise ValueError(f"Nguồn dữ liệu không được hỗ trợ: {data_source}")
    return list(metadata[data_source]["feature_columns"])


def _load_model(data_source: str):
    """Tải lười pipeline để server vẫn khởi động được trước khi có request."""
    if data_source not in _models:
        model_path = MODEL_DIR / f"{data_source}_ml.joblib"
        if not model_path.exists():
            raise RuntimeError(f"Không tìm thấy pipeline: {model_path}")
        _models[data_source] = joblib.load(model_path)
    return _models[data_source]


def _humanize_feature(feature_name: str) -> str:
    """Chuyển tên đặc trưng kỹ thuật thành chuỗi dễ đọc hơn."""
    return feature_name.replace("_", " ").replace("  ", " ").strip()


def _explain_with_contributions(pipeline, frame: pd.DataFrame) -> list[str]:
    """Lấy tối đa năm đặc trưng đóng góp nhiều nhất về phía lớp Dropout."""
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]
    feature_names = preprocessor.get_feature_names_out()
    transformed = preprocessor.transform(frame)
    if hasattr(transformed, "toarray"):
        values = transformed.toarray()[0]
    else:
        values = np.asarray(transformed)[0]

    if hasattr(classifier, "coef_"):
        contributions = values * classifier.coef_[0]
    elif hasattr(classifier, "feature_importances_"):
        contributions = values * classifier.feature_importances_
    else:
        return ["Mô hình không cung cấp mức đóng góp của đặc trưng"]

    positive_indices = np.where(contributions > 0)[0]
    if len(positive_indices) > 0:
        ranked = positive_indices[np.argsort(contributions[positive_indices])[::-1]]
    else:
        ranked = np.argsort(np.abs(contributions))[::-1]
    return [_humanize_feature(feature_names[index]) for index in ranked[:5]]


def _build_recommendations(factors: list[str]) -> list[str]:
    """Ánh xạ các nhóm yếu tố sang hành động hỗ trợ có thể thực hiện."""
    recommendations: list[str] = []
    joined = " ".join(factors).lower()
    if any(token in joined for token in ["gpa", "grade", "approved", "curricular"]):
        recommendations.append("Sắp xếp buổi tư vấn học vụ và lập kế hoạch cải thiện kết quả học tập")
    if any(token in joined for token in ["attendance", "evaluations", "study hours"]):
        recommendations.append("Liên hệ sinh viên để rà soát mức độ tham gia học tập")
    if any(token in joined for token in ["tuition", "debtor", "income", "scholarship"]):
        recommendations.append("Rà soát nhu cầu hỗ trợ học phí hoặc tài chính")
    if "stress" in joined:
        recommendations.append("Đề xuất tư vấn tâm lý và theo dõi sức khỏe tinh thần")
    if not recommendations:
        recommendations.append("Tư vấn viên cần rà soát các yếu tố nổi bật và theo dõi sinh viên định kỳ")
    return list(dict.fromkeys(recommendations))


def predict(features: dict[str, Any], data_source: str) -> dict[str, Any]:
    """Dự đoán nguy cơ bỏ học cho một sinh viên bằng pipeline của nguồn đã chọn."""
    feature_columns = required_fields(data_source)
    missing_columns = [column for column in feature_columns if column not in features]
    if missing_columns:
        raise ValueError(f"Thiếu trường bắt buộc cho {data_source}: {missing_columns}")

    pipeline = _load_model(data_source)
    frame = pd.DataFrame([{column: features.get(column) for column in feature_columns}])
    probability = float(pipeline.predict_proba(frame)[0, 1])
    threshold = float(_load_metadata()[data_source]["threshold"])
    high_threshold = max(0.60, min(0.90, threshold + 0.20))

    if probability < threshold:
        risk_level = "low"
    elif probability < high_threshold:
        risk_level = "medium"
    else:
        risk_level = "high"

    factors = _explain_with_contributions(pipeline, frame)
    return {
        "prediction": "Dropout" if probability >= threshold else "No Dropout",
        "risk_score": probability,
        "risk_level": risk_level,
        "risk_factors": factors,
        "recommendations": _build_recommendations(factors),
        "score_type": "probability",
    }
