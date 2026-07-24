import { useMemo, useState } from "react";
import { apiClient } from "../api/client";
import type { DataSource, PredictionType, RiskAssessment } from "../types";
import "./ChatPanel.css";
import "./FormPanel.css";

type FieldType = "number" | "select";

interface FieldDef {
  name: string;
  label: string;
  type: FieldType;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  hint?: string;
}

// Field metadata mirrors the training data (see BE risk_service.required_fields
// and data/student_dropout.csv value ranges). Manual entry is only offered for
// the student_dropout source; student_dropout_and_success has 34 features and is
// handled via Upload instead.
const FIELD_DEFS: Record<string, FieldDef> = {
  Gender: { name: "Gender", label: "Gender", type: "select", options: ["Male", "Female"] },
  Internet_Access: { name: "Internet_Access", label: "Internet access", type: "select", options: ["Yes", "No"] },
  Part_Time_Job: { name: "Part_Time_Job", label: "Part-time job", type: "select", options: ["Yes", "No"] },
  Scholarship: { name: "Scholarship", label: "Scholarship", type: "select", options: ["Yes", "No"] },
  Semester: { name: "Semester", label: "Year of study", type: "select", options: ["Year 1", "Year 2", "Year 3", "Year 4"] },
  Department: { name: "Department", label: "Department", type: "select", options: ["Arts", "Business", "CS", "Engineering", "Science"] },
  Parental_Education: {
    name: "Parental_Education",
    label: "Parental education",
    type: "select",
    options: ["None", "High School", "Bachelor", "Master", "PhD"],
  },
  Age: { name: "Age", label: "Age", type: "number", min: 15, max: 60, step: 0.1, placeholder: "e.g. 20" },
  Family_Income: { name: "Family_Income", label: "Family income", type: "number", min: 0, step: 1000, placeholder: "e.g. 60000" },
  Study_Hours_per_Day: { name: "Study_Hours_per_Day", label: "Study hours / day", type: "number", min: 0, max: 24, step: 0.1, placeholder: "e.g. 3" },
  Attendance_Rate: { name: "Attendance_Rate", label: "Attendance rate (%)", type: "number", min: 0, max: 100, step: 0.1, placeholder: "0–100" },
  Assignment_Delay_Days: { name: "Assignment_Delay_Days", label: "Assignment delay (days)", type: "number", min: 0, step: 1, placeholder: "e.g. 2" },
  Travel_Time_Minutes: { name: "Travel_Time_Minutes", label: "Travel time (min)", type: "number", min: 0, step: 1, placeholder: "e.g. 30" },
  Stress_Index: { name: "Stress_Index", label: "Stress index (1–10)", type: "number", min: 1, max: 10, step: 1, placeholder: "1–10" },
  GPA: { name: "GPA", label: "GPA", type: "number", min: 0, max: 4, step: 0.01, placeholder: "0–4" },
  Semester_GPA: { name: "Semester_GPA", label: "Semester GPA", type: "number", min: 0, max: 4, step: 0.01, placeholder: "0–4" },
  CGPA: { name: "CGPA", label: "CGPA", type: "number", min: 0, max: 4, step: 0.01, placeholder: "0–4" },
};

const RULE_BASED_ORDER = [
  "GPA", "Attendance_Rate", "Stress_Index", "Study_Hours_per_Day",
  "Assignment_Delay_Days", "Internet_Access", "Part_Time_Job",
];
const ML_ORDER = [
  "GPA", "Semester_GPA", "CGPA", "Attendance_Rate", "Study_Hours_per_Day",
  "Assignment_Delay_Days", "Stress_Index", "Travel_Time_Minutes",
  "Age", "Family_Income", "Gender", "Department", "Semester",
  "Parental_Education", "Scholarship", "Internet_Access", "Part_Time_Job",
];

function fieldsFor(predictionType: PredictionType): FieldDef[] {
  const order = predictionType === "ml" ? ML_ORDER : RULE_BASED_ORDER;
  return order.map((name) => FIELD_DEFS[name]);
}

interface FormPanelProps {
  dataSource: DataSource;
  predictionType: PredictionType;
}

export function FormPanel({ dataSource, predictionType }: FormPanelProps) {
  const [name, setName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RiskAssessment | null>(null);

  const supportsManualEntry = dataSource === "student_dropout";
  const fields = useMemo(() => fieldsFor(predictionType), [predictionType]);

  if (!supportsManualEntry) {
    return (
      <div className="form-panel">
        <div className="form-panel__notice">
          <span className="form-panel__notice-title">Manual entry isn't available for this dataset</span>
          <p>
            <code>student_dropout_and_success.csv</code> has 34 features, so manual form entry isn't
            practical. Switch to <strong>Upload file</strong> to assess this dataset, or select the{" "}
            <code>student_dropout</code> source in the experiment controls.
          </p>
        </div>
      </div>
    );
  }

  function setValue(fieldName: string, value: string) {
    setValues((prev) => ({ ...prev, [fieldName]: value }));
  }

  function resetForm() {
    setValues({});
    setName("");
    setStudentId("");
    setResult(null);
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const missing = fields.filter((f) => !(values[f.name] ?? "").trim());
    if (missing.length > 0) {
      setError(`Please fill in every field (${missing.length} remaining).`);
      return;
    }

    const payload: Record<string, string | number> = {};
    for (const f of fields) {
      const raw = values[f.name].trim();
      payload[f.name] = f.type === "number" ? Number(raw) : raw;
    }

    setError(null);
    setIsSubmitting(true);
    setResult(null);
    try {
      const response = await apiClient.predictForm({
        dataSource,
        predictionType,
        fields: payload,
        name: name.trim() || undefined,
        studentId: studentId.trim() || undefined,
      });
      setResult(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Assessment failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="form-panel">
      <form className="form-panel__form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="form-field">
            <span className="form-field__label">Student name <span className="form-field__optional">(optional)</span></span>
            <input
              className="form-field__input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Jane Doe"
            />
          </label>
          <label className="form-field">
            <span className="form-field__label">Student ID <span className="form-field__optional">(optional)</span></span>
            <input
              className="form-field__input"
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="e.g. SV001"
            />
          </label>

          {fields.map((f) => (
            <label className="form-field" key={f.name}>
              <span className="form-field__label">{f.label}</span>
              {f.type === "select" ? (
                <select
                  className="form-field__input"
                  value={values[f.name] ?? ""}
                  onChange={(e) => setValue(f.name, e.target.value)}
                >
                  <option value="" disabled>
                    Select…
                  </option>
                  {f.options!.map((opt) => (
                    <option value={opt} key={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  className="form-field__input"
                  type="number"
                  inputMode="decimal"
                  value={values[f.name] ?? ""}
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  placeholder={f.placeholder}
                  onChange={(e) => setValue(f.name, e.target.value)}
                />
              )}
            </label>
          ))}
        </div>

        {error && <div className="form-panel__error">{error}</div>}

        <div className="form-panel__actions">
          <button type="button" className="form-panel__reset" onClick={resetForm} disabled={isSubmitting}>
            Reset
          </button>
          <button type="submit" className="form-panel__submit" disabled={isSubmitting}>
            {isSubmitting ? "Assessing…" : "Assess risk"}
          </button>
        </div>
      </form>

      {result && (
        <div className="result-card form-panel__result">
          <div className={`result-card__header result-card__header--${result.riskLevel}`}>
            <span className="result-card__risk">
              {result.riskLevel === "high" ? "High" : result.riskLevel === "medium" ? "Medium" : "Low"} risk ·{" "}
              {Math.round(result.riskProb * 100)}%
            </span>
            <span className="result-card__status-pill">{result.statusLabel}</span>
          </div>
          <div className="result-card__body">
            <div className="result-card__section-label">Recommended intervention</div>
            <div className="result-card__recommendation">{result.recommendation}</div>
            <div className="result-card__section-label">Why</div>
            <div className="result-card__factors">
              {result.factors.map((factor) => (
                <div className="result-card__factor" key={factor}>
                  <span className="result-card__bullet">•</span>
                  <span>{factor}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
