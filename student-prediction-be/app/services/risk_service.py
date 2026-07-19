from student_prediction import calculate_risk
from app.services import ml_service


def assess(fields: dict, prediction_type: str) -> dict:
    """
    Unified risk assessment. Routes to ML or rule-based based on prediction_type.
    Returns a dict matching RiskAssessmentSchema.
    """
    if prediction_type == "ml":
        return ml_service.predict(fields)

    # Rule-based path
    result = calculate_risk(fields)
    risk_level = result["risk_level"]  # "Cao", "Trung bình", or "Thấp"

    level_map = {
        "Cao": "high",
        "Trung bình": "medium",
        "Thấp": "low",
    }
    # Phase 1: 2-class mapping (3-class Enrolled deferred)
    status_map = {
        "Cao": "Dropout",
        "Trung bình": "Graduate",
        "Thấp": "Graduate",
    }

    return {
        "statusLabel": status_map[risk_level],
        "riskLevel": level_map[risk_level],
        "riskProb": min(result["risk_score"] / 11.0, 1.0),
        "recommendation": "; ".join(result["recommendations"]),
        "factors": result["risk_reasons"],
    }
