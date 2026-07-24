"""Orchestrates the two data sources and the two prediction solution types."""

from typing import Any

from app.services import ml_service, rule_service


DATA_SOURCES = ("student_dropout_and_success", "student_dropout")
PREDICTION_TYPES = ("ml", "rule_based")


def validate_selection(data_source: str, prediction_type: str) -> None:
    """Validate the (data source, solution) pair sent by the client."""
    if data_source not in DATA_SOURCES:
        raise ValueError(
            f"dataSource must be one of: {list(DATA_SOURCES)}"
        )
    if prediction_type not in PREDICTION_TYPES:
        raise ValueError(
            f"predictionType must be one of: {list(PREDICTION_TYPES)}"
        )


def required_fields(data_source: str, prediction_type: str) -> list[str]:
    """Return the input schema for the exact (source, solution) pair."""
    validate_selection(data_source, prediction_type)
    if prediction_type == "ml":
        return ml_service.required_fields(data_source)
    return rule_service.required_fields(data_source)


def assess(
    fields: dict[str, Any], prediction_type: str, data_source: str
) -> dict[str, Any]:
    """Assess risk and return the standard contract plus legacy-compatible fields."""
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
        # Standard fields used by the new integration.
        "dataSource": data_source,
        "solutionType": prediction_type,
        "prediction": prediction,
        "riskScore": score,
        "riskLevel": result["risk_level"],
        "riskFactors": factors,
        "recommendations": recommendations,
        "scoreType": result["score_type"],
        # Fields kept compatible with the older UI and data.
        "statusLabel": prediction,
        "riskProb": score,
        "factors": factors,
        "recommendation": "; ".join(recommendations),
    }
