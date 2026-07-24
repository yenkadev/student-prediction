"""Prediction using the Machine Learning pipelines finalized in the experiments."""

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
    """Read the metadata once and cache it in the backend process memory."""
    global _metadata
    if _metadata is None:
        if not METADATA_PATH.exists():
            raise RuntimeError(
                "outputs/models/ml_model_metadata.json not found. "
                "Run the Machine Learning notebook first."
            )
        with METADATA_PATH.open(encoding="utf-8") as file:
            _metadata = json.load(file)
    return _metadata


def supported_data_sources() -> tuple[str, ...]:
    """Return the two data sources that have a trained model."""
    return tuple(_load_metadata().keys())


def required_fields(data_source: str) -> list[str]:
    """Return the exact feature order a source's pipeline expects."""
    metadata = _load_metadata()
    if data_source not in metadata:
        raise ValueError(f"Unsupported data source: {data_source}")
    return list(metadata[data_source]["feature_columns"])


def _load_model(data_source: str):
    """Lazily load the pipeline so the server can start before any request."""
    if data_source not in _models:
        model_path = MODEL_DIR / f"{data_source}_ml.joblib"
        if not model_path.exists():
            raise RuntimeError(f"Pipeline not found: {model_path}")
        _models[data_source] = joblib.load(model_path)
    return _models[data_source]


def _humanize_feature(feature_name: str) -> str:
    """Turn a technical feature name into a more readable string."""
    return feature_name.replace("_", " ").replace("  ", " ").strip()


def _explain_with_contributions(pipeline, frame: pd.DataFrame) -> list[str]:
    """Take up to five features contributing most towards the Dropout class."""
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
        return ["The model does not provide feature contributions"]

    positive_indices = np.where(contributions > 0)[0]
    if len(positive_indices) > 0:
        ranked = positive_indices[np.argsort(contributions[positive_indices])[::-1]]
    else:
        ranked = np.argsort(np.abs(contributions))[::-1]
    return [_humanize_feature(feature_names[index]) for index in ranked[:5]]


def _build_recommendations(factors: list[str]) -> list[str]:
    """Map groups of factors to actionable support steps."""
    recommendations: list[str] = []
    joined = " ".join(factors).lower()
    if any(token in joined for token in ["gpa", "grade", "approved", "curricular"]):
        recommendations.append("Arrange academic advising and a plan to improve academic results")
    if any(token in joined for token in ["attendance", "evaluations", "study hours"]):
        recommendations.append("Reach out to the student to review their engagement in class")
    if any(token in joined for token in ["tuition", "debtor", "income", "scholarship"]):
        recommendations.append("Review the need for tuition or financial support")
    if "stress" in joined:
        recommendations.append("Recommend counseling and monitor mental well-being")
    if not recommendations:
        recommendations.append("An advisor should review the top factors and monitor the student regularly")
    return list(dict.fromkeys(recommendations))


def predict(features: dict[str, Any], data_source: str) -> dict[str, Any]:
    """Predict dropout risk for a single student using the selected source's pipeline."""
    feature_columns = required_fields(data_source)
    missing_columns = [column for column in feature_columns if column not in features]
    if missing_columns:
        raise ValueError(f"Missing required fields for {data_source}: {missing_columns}")

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
