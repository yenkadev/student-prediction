import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { OverviewActivityItem } from "../api/types";
import type { RiskLevel } from "../types";
import { initialsOf } from "../types";
import { RiskBadge } from "./RiskBadge";
import "./AllStudents.css";

interface AllStudentsProps {
  onSelectStudent: (id: string) => void;
  filterRisk?: RiskLevel;
}

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} minute${mins === 1 ? "" : "s"} ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hour${hrs === 1 ? "" : "s"} ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

const FILTER_LABEL: Record<RiskLevel, string> = {
  low: "Low risk",
  medium: "Medium risk",
  high: "High risk",
};

export function AllStudents({ onSelectStudent, filterRisk }: AllStudentsProps) {
  const [students, setStudents] = useState<OverviewActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.getAllStudents()
      .then((res) => { setStudents(res.students); setLoading(false); })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load students");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="ast-empty">Loading…</div>;
  if (error) return <div className="ast-error">{error}</div>;

  const displayed = filterRisk ? students.filter((s) => s.riskLevel === filterRisk) : students;

  if (displayed.length === 0) return <div className="ast-empty">No assessed students yet.</div>;

  return (
    <div>
      {filterRisk && (
        <div className="ast-filter-bar">
          <span className={`ast-filter-chip ast-filter-chip--${filterRisk}`}>
            {FILTER_LABEL[filterRisk]}
          </span>
          <span className="ast-filter-count">{displayed.length} student{displayed.length === 1 ? "" : "s"}</span>
        </div>
      )}
      <div className="ast-list">
        {displayed.map((student) => (
          <div
            key={student.id}
            className="ast-row"
            onClick={() => onSelectStudent(student.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && onSelectStudent(student.id)}
          >
            <div className="ast-row__info">
              <div className="ast-avatar">{initialsOf(student.name)}</div>
              <div>
                <div className="ast-row__name">{student.name}</div>
                <div className="ast-row__meta">
                  {timeAgo(student.assessedAt)} · {student.statusLabel}
                </div>
              </div>
            </div>
            <RiskBadge level={student.riskLevel} />
          </div>
        ))}
      </div>
    </div>
  );
}
