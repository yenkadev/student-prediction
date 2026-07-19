import { useMemo, useState } from "react";
import { initialsOf, type RiskLevel, type Student } from "../types";
import { RiskBadge } from "./RiskBadge";
import "./BatchResults.css";

type FilterLevel = "all" | RiskLevel;

interface BatchResultsProps {
  students: Student[];
  onGoToUpload: () => void;
  onToggleReviewed: (id: string) => void;
  onSelectStudent: (id: string) => void;
}

const FILTERS: { value: FilterLevel; label: string }[] = [
  { value: "all", label: "All" },
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

function exportCsv(students: Student[]) {
  const header = "Student,Student ID,Predicted,Risk %,Risk Level,Recommendation\n";
  const body = students
    .map((s) =>
      [
        s.name,
        s.studentId,
        s.assessment.statusLabel,
        `${Math.round(s.assessment.riskProb * 100)}%`,
        s.assessment.riskLevel,
        `"${s.assessment.recommendation}"`,
      ].join(","),
    )
    .join("\n");
  const blob = new Blob([header + body], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "risk-warning-batch-results.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function BatchResults({ students, onGoToUpload, onToggleReviewed, onSelectStudent }: BatchResultsProps) {
  const [filter, setFilter] = useState<FilterLevel>("all");
  const [sortDesc, setSortDesc] = useState(true);

  const visibleRows = useMemo(() => {
    let rows = students.filter((s) => filter === "all" || s.assessment.riskLevel === filter);
    rows = rows
      .slice()
      .sort((a, b) => (sortDesc ? b.assessment.riskProb - a.assessment.riskProb : a.assessment.riskProb - b.assessment.riskProb));
    return rows;
  }, [students, filter, sortDesc]);

  if (students.length === 0) {
    return (
      <div className="batch-empty">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C7C2B4" strokeWidth="1.6">
          <path d="M3 3h18v18H3z" />
          <path d="M3 9h18M3 15h18M9 3v18" />
        </svg>
        <div className="batch-empty__text">No batch results yet. Upload a file from New Assessment to see students here.</div>
        <button type="button" className="batch-empty__btn" onClick={onGoToUpload}>
          Upload a file
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="batch-toolbar">
        <div className="batch-toolbar__left">
          <div className="filter-group">
            {FILTERS.map((f) => (
              <button
                key={f.value}
                type="button"
                className={`filter-btn${filter === f.value ? " filter-btn--active" : ""} filter-btn--${f.value}`}
                onClick={() => setFilter(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
          <button type="button" className="sort-btn" onClick={() => setSortDesc((v) => !v)}>
            Sort by risk
            <span>{sortDesc ? "↓" : "↑"}</span>
          </button>
        </div>
        <button type="button" className="export-btn" onClick={() => exportCsv(visibleRows)}>
          Export CSV
        </button>
      </div>

      <div className="batch-table">
        <div className="batch-table__head">
          <div>Student</div>
          <div>Predicted</div>
          <div>Risk</div>
          <div>Recommendation</div>
          <div />
        </div>
        {visibleRows.map((row) => (
          <div
            key={row.id}
            className="batch-row"
            onClick={() => onSelectStudent(row.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && onSelectStudent(row.id)}
          >
            <div className="batch-row__student">
              <div className="avatar avatar--sm">{initialsOf(row.name)}</div>
              <div>
                <div className="batch-row__name">{row.name}</div>
                <div className="batch-row__id">{row.studentId}</div>
              </div>
            </div>
            <div className="batch-row__predicted">{row.assessment.statusLabel}</div>
            <div>
              <RiskBadge level={row.assessment.riskLevel} riskProb={row.assessment.riskProb} short />
            </div>
            <div className="batch-row__recommendation">{row.assessment.recommendation}</div>
            <button
              type="button"
              className={`reviewed-icon-btn${row.reviewed ? " reviewed-icon-btn--done" : ""}`}
              title={row.reviewed ? "Reviewed" : "Mark as reviewed"}
              onClick={(e) => {
                e.stopPropagation();
                onToggleReviewed(row.id);
              }}
            >
              {row.reviewed ? "✓" : "○"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
