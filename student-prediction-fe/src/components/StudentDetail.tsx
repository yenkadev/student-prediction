import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { StudentDetailResponse } from "../api/types";
import type { Student } from "../types";
import { initialsOf } from "../types";
import { RiskBadge } from "./RiskBadge";
import "./StudentDetail.css";

const FEATURE_LABELS: Record<string, string> = {
  GPA: "GPA",
  Attendance_Rate: "Attendance Rate (%)",
  Stress_Index: "Stress Index",
  Study_Hours_per_Day: "Study Hours / Day",
  Assignment_Delay_Days: "Assignment Delay (days)",
  Internet_Access: "Internet Access",
  Part_Time_Job: "Part-Time Job",
  Gender: "Gender",
  Age: "Age",
  Family_Income: "Family Income",
  Scholarship: "Scholarship",
  Semester: "Semester",
  Department: "Department",
  Parental_Education: "Parental Education",
  Travel_Time_Minutes: "Travel Time (min)",
  Semester_GPA: "Semester GPA",
  CGPA: "CGPA",
  "Curricular units 1st sem (enrolled)": "1st sem units enrolled",
  "Curricular units 1st sem (approved)": "1st sem units approved",
  "Curricular units 2nd sem (enrolled)": "2nd sem units enrolled",
  "Curricular units 2nd sem (approved)": "2nd sem units approved",
  "Curricular units 2nd sem (grade)": "2nd sem average grade",
  "Curricular units 2nd sem (without evaluations)": "2nd sem units without evaluations",
  "Tuition fees up to date": "Tuition fees up to date",
  Debtor: "Debtor",
};

const FEATURE_ORDER = Object.keys(FEATURE_LABELS);

function formatDate(iso: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatValue(val: unknown): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "number") return val.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return String(val);
}

interface StudentDetailProps {
  studentId: string;
  batchStudent?: Student;
  onBack: () => void;
}

function detailFromBatch(student: Student): StudentDetailResponse {
  return {
    id: student.id,
    name: student.name,
    studentId: student.studentId,
    source: "batch",
    reviewed: student.reviewed ?? false,
    assessed_at: student.assessed_at ?? "",
    assessment: student.assessment,
    features: student.features ?? null,
  };
}

export function StudentDetail({ studentId, batchStudent, onBack }: StudentDetailProps) {
  const [detail, setDetail] = useState<StudentDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);

    // Synchronous upload results already carry all the data, so no MongoDB query is needed.
    if (batchStudent) {
      setDetail(detailFromBatch(batchStudent));
      return;
    }

    setDetail(null);
    apiClient
      .getStudent(studentId)
      .then(setDetail)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load student")
      );
  }, [studentId, batchStudent]);

  return (
    <div className="student-detail">
      <button type="button" className="student-detail__back" onClick={onBack}>
        ← Back
      </button>

      {error && <div className="student-detail__error">{error}</div>}

      {!error && !detail && <div className="student-detail__loading">Loading…</div>}

      {detail && (
        <>
          {/* Student identification */}
          <div className="sd-header">
            <div className="avatar avatar--lg">{initialsOf(detail.name)}</div>
            <div className="sd-header__info">
              <div className="sd-header__name">{detail.name}</div>
              <div className="sd-header__id">ID: {detail.studentId}</div>
              <div className="sd-header__meta">
                Assessed {formatDate(detail.assessed_at)} · via {detail.source === "batch" ? "Batch upload" : detail.source === "form" ? "Form" : "Chat"}
              </div>
            </div>
            <RiskBadge level={detail.assessment.riskLevel} />
          </div>

          {/* Risk assessment result */}
          <div className="sd-card">
            <div className="sd-card__title">Risk Assessment</div>
            <div className="sd-assess-grid">
              <div className="sd-assess-item">
                <div className="sd-assess-item__label">Predicted status</div>
                <div className="sd-assess-item__value">{detail.assessment.statusLabel}</div>
              </div>
              <div className="sd-assess-item">
                <div className="sd-assess-item__label">Risk level</div>
                <div className="sd-assess-item__value sd-assess-item__value--capitalize">{detail.assessment.riskLevel}</div>
              </div>
              <div className="sd-assess-item">
                <div className="sd-assess-item__label">Data source</div>
                <div className="sd-assess-item__value">{detail.assessment.dataSource}.csv</div>
              </div>
              <div className="sd-assess-item">
                <div className="sd-assess-item__label">Solution</div>
                <div className="sd-assess-item__value">
                  {detail.assessment.solutionType === "ml" ? "Machine Learning" : "Rule-based Scoring"}
                </div>
              </div>
              <div className="sd-assess-item sd-assess-item--full">
                <div className="sd-assess-item__label">
                  {detail.assessment.scoreType === "probability" ? "Risk probability" : "Normalized rule score"}
                </div>
                <div className="sd-prob-row">
                  <div className="sd-prob-track">
                    <div
                      className={`sd-prob-fill sd-prob-fill--${detail.assessment.riskLevel}`}
                      style={{ width: `${Math.round(detail.assessment.riskProb * 100)}%` }}
                    />
                  </div>
                  <span className="sd-prob-pct">{Math.round(detail.assessment.riskProb * 100)}%</span>
                </div>
              </div>
              <div className="sd-assess-item sd-assess-item--full">
                <div className="sd-assess-item__label">Recommendation</div>
                <ul className="sd-factors">
                  {detail.assessment.recommendations.map((recommendation) => (
                    <li key={recommendation}>{recommendation}</li>
                  ))}
                </ul>
              </div>
              <div className="sd-assess-item sd-assess-item--full">
                <div className="sd-assess-item__label">Key risk factors</div>
                <ul className="sd-factors">
                  {detail.assessment.riskFactors.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Input data used for the assessment */}
          {detail.features ? (
            <div className="sd-card">
              <div className="sd-card__title">Academic Data</div>
              <div className="sd-features-grid">
                {FEATURE_ORDER.map((key) => {
                  const val = (detail.features as Record<string, unknown>)?.[key];
                  if (val === undefined) return null;
                  return (
                    <div className="sd-feature-row" key={key}>
                      <div className="sd-feature-row__label">{FEATURE_LABELS[key]}</div>
                      <div className="sd-feature-row__value">{formatValue(val)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="sd-no-features">Academic data not available for this record.</p>
          )}
        </>
      )}
    </div>
  );
}
