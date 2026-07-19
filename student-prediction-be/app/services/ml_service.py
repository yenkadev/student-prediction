import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)

_CATEGORICAL_FEATURES = [
    "Gender",
    "Internet_Access",
    "Part_Time_Job",
    "Scholarship",
    "Semester",
    "Department",
    "Parental_Education",
]

_BASE = Path(__file__).parent.parent.parent  # student-prediction-BE/

try:
    _model = joblib.load(_BASE / "models/lgbm_model.joblib")
    with open(_BASE / "models/feature_names.json") as f:
        _feature_names: list[str] = json.load(f)
    _explainer = shap.TreeExplainer(_model)
except FileNotFoundError:
    raise RuntimeError("ML model not found. Run scripts/train_model.py first.")


def _build_recommendation(prob: float) -> str:
    if prob > 0.6:
        return "Immediate intervention required. Connect student with academic advisor and counseling services."
    if prob >= 0.3:
        return "Monitor closely. Schedule check-in meeting and review study plan."
    return "Student is on track. Continue regular academic monitoring."


def predict(features: dict) -> dict:
    df = pd.DataFrame([features], columns=_feature_names)

    for col in _CATEGORICAL_FEATURES:
        df[col] = df[col].astype("category")

    logger.debug("🟦 [ML:INPUT] DataFrame:\n%s", df.to_string())

    proba = _model.predict_proba(df)
    prob = float(proba[0][1])
    logger.debug(
        "🟩 [ML:OUTPUT]\n"
        "  p_stay    = %.4f\n"
        "  p_dropout = %.4f",
        proba[0][0], proba[0][1],
    )

    shap_vals = _explainer(df)

    raw = shap_vals.values
    if raw.ndim == 3:
        class1_shap = raw[0, :, 1]
    else:
        class1_shap = raw[0, :]

    top5_indices = np.argsort(np.abs(class1_shap))[::-1][:5]
    factors: list[str] = [_feature_names[i] for i in top5_indices]

    shap_summary = {_feature_names[i]: round(float(class1_shap[i]), 4) for i in top5_indices}
    shap_lines = "\n".join(f"  {k}: {v:+.4f}" for k, v in shap_summary.items())
    logger.debug("🟧 [ML:SHAP] top 5 toward Dropout:\n%s", shap_lines)

    result = {
        "statusLabel": "Dropout" if prob > 0.5 else "Graduate",
        "riskLevel": "high" if prob > 0.6 else ("medium" if prob >= 0.3 else "low"),
        "riskProb": round(prob, 4),
        "recommendation": _build_recommendation(prob),
        "factors": factors,
    }
    logger.debug(
        "🟪 [ML:RESPONSE]\n"
        "  statusLabel    = %s\n"
        "  riskLevel      = %s\n"
        "  riskProb       = %.4f\n"
        "  factors        = %s\n"
        "  recommendation = %s",
        result["statusLabel"], result["riskLevel"], result["riskProb"],
        result["factors"], result["recommendation"],
    )
    return result
