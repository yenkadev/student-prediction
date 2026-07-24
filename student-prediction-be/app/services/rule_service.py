"""The two risk-scoring rule sets finalized from the experiments."""

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
    """Load the scoring config and thresholds selected on the validation set."""
    global _config
    if _config is None:
        if not CONFIG_PATH.exists():
            raise RuntimeError(
                "outputs/rules/rule_based_config.json not found. "
                "Run the Rule-based Scoring notebook first."
            )
        with CONFIG_PATH.open(encoding="utf-8") as file:
            _config = json.load(file)
    return _config


def required_fields(data_source: str) -> list[str]:
    """Return the input fields expected by the matching rule set."""
    if data_source not in REQUIRED_FIELDS:
        raise ValueError(f"Unsupported data source: {data_source}")
    return list(REQUIRED_FIELDS[data_source])


def _is_missing(value: Any) -> bool:
    """Detect None and NaN coming from JSON, CSV or pandas data."""
    return value is None or (isinstance(value, float) and math.isnan(value))


def _read_numeric(fields: Mapping[str, Any], field: str, data_source: str) -> float:
    """Read a numeric field, falling back to the train-learned imputation value."""
    if field not in fields:
        raise ValueError(f"Missing required field: {field}")
    value = fields[field]
    if _is_missing(value):
        value = _load_config()[data_source]["imputation_values_from_train"][field]
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be a numeric value") from error


def _read_yes_no(fields: Mapping[str, Any], field: str, data_source: str) -> str:
    """Read a Yes/No field and normalize its casing."""
    if field not in fields:
        raise ValueError(f"Missing required field: {field}")
    value = fields[field]
    if _is_missing(value):
        value = _load_config()[data_source]["imputation_values_from_train"][field]
    normalized = str(value).strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValueError(f"{field} only accepts 'Yes' or 'No'")
    return normalized


def _score_source_1(fields: Mapping[str, Any]) -> tuple[int, list[str], list[str]]:
    """Score the academic and financial data of Source 1."""
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
        factors.append("2nd-semester pass rate below 50%")
        recommendations.append("Provide academic advising and a plan to retake failed courses")
    elif ratio_2 < 0.75:
        score += 1
        factors.append("2nd-semester pass rate below 75%")
        recommendations.append("Monitor course completion progress next semester")

    if grade_2 < 10:
        score += 2
        factors.append("2nd-semester average grade below 10")
        recommendations.append("Arrange academic support for low-performing courses")
    elif grade_2 < 12:
        score += 1
        factors.append("2nd-semester average grade below 12")
        recommendations.append("Monitor academic results next semester")

    if ratio_1 < 0.50:
        score += 2
        factors.append("1st-semester pass rate below 50%")
        recommendations.append("Review failed foundational courses")
    elif ratio_1 < 0.75:
        score += 1
        factors.append("1st-semester pass rate below 75%")
        recommendations.append("Monitor completion of outstanding courses")

    if tuition_up_to_date == 0:
        score += 2
        factors.append("Tuition fees not paid on time")
        recommendations.append("Reach out about tuition advising and financial support options")
    if debtor == 1:
        score += 1
        factors.append("Student currently has outstanding debt")
        recommendations.append("Review the debt status and a repayment plan")
    if without_evaluations >= 2:
        score += 1
        factors.append("Missed evaluations in at least 2 courses in the 2nd semester")
        recommendations.append("Reach out to confirm the reason for the missed evaluations")

    return score, factors, recommendations


def _score_source_2(fields: Mapping[str, Any]) -> tuple[int, list[str], list[str]]:
    """Score the study behaviour and conditions of Source 2."""
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
        factors.append("GPA below 2.0")
        recommendations.append("Provide academic advising and a GPA improvement plan")
    elif gpa < 2.5:
        score += 1
        factors.append("GPA between 2.0 and 2.5")
        recommendations.append("Monitor academic results next semester")
    if attendance < 75:
        score += 2
        factors.append("Attendance rate below 75%")
        recommendations.append("Reach out to the student and identify the reason for absences")
    elif attendance < 85:
        score += 1
        factors.append("Attendance rate between 75% and 85%")
        recommendations.append("Monitor attendance and encourage full class attendance")
    if stress >= 7:
        score += 2
        factors.append("High stress level")
        recommendations.append("Recommend counseling and monitor mental well-being")
    elif stress >= 5:
        score += 1
        factors.append("Stress level to keep an eye on")
        recommendations.append("Monitor the stress level regularly")
    if study_hours < 2:
        score += 1
        factors.append("Less than 2 hours of self-study per day")
        recommendations.append("Help build a study schedule")
    if delay >= 3:
        score += 1
        factors.append("Assignments submitted 3 or more days late")
        recommendations.append("Send deadline reminders and support time-management skills")
    if internet == "no":
        score += 1
        factors.append("No reliable internet access")
        recommendations.append("Provide a device or an internet access location")
    if part_time_job == "yes":
        score += 1
        factors.append("Part-time job may affect studies")
        recommendations.append("Advise on balancing part-time work and studying")
    return score, factors, recommendations


def predict(features: Mapping[str, Any], data_source: str) -> dict[str, Any]:
    """Score a single student and apply the thresholds fixed on the validation set."""
    missing_fields = [field for field in required_fields(data_source) if field not in features]
    if missing_fields:
        raise ValueError(f"Missing required fields for {data_source}: {missing_fields}")

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
        factors = ["No significant risk factors detected"]
        recommendations = ["Continue regular monitoring"]

    return {
        "prediction": "Dropout" if raw_score >= alert_threshold else "No Dropout",
        "risk_score": normalized_score,
        "risk_level": risk_level,
        "risk_factors": factors,
        "recommendations": list(dict.fromkeys(recommendations)),
        "score_type": "normalized_rule_score",
    }
