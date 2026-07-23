import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { OverviewResponse, RecentSessionItem } from "../api/types";
import type { RiskLevel } from "../types";
import { initialsOf } from "../types";
import { RiskBadge } from "./RiskBadge";
import "./Dashboard.css";

interface DashboardProps {
  onStartChat: () => void;
  onStartUpload: () => void;
  onSelectStudent: (id: string) => void;
  onViewBatch: (jobId: string) => void;
  onContinueChat: (conversationId: string) => void;
  onViewAllSessions: () => void;
  onViewAllStudents: (filter?: RiskLevel) => void;
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

function SessionIcon({ type }: { type: RecentSessionItem["type"] }) {
  if (type === "batch") {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    );
  }
  if (type === "form") {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="4" y="3" width="16" height="18" rx="2" />
        <line x1="8" y1="8" x2="16" y2="8" />
        <line x1="8" y1="12" x2="16" y2="12" />
        <line x1="8" y1="16" x2="13" y2="16" />
      </svg>
    );
  }
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
  );
}

function StatusChip({ status }: { status: RecentSessionItem["status"] }) {
  return (
    <span className={`status-chip status-chip--${status}`}>
      {status === "done" ? "Done" : status === "in_progress" ? "In progress" : "Failed"}
    </span>
  );
}

export function Dashboard({ onStartChat, onStartUpload, onSelectStudent, onViewBatch, onContinueChat, onViewAllSessions, onViewAllStudents }: DashboardProps) {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  useEffect(() => {
    apiClient.getOverview()
      .then(setOverview)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load overview"));
  }, []);

  async function deleteSession(session: RecentSessionItem) {
    try {
      if (session.type === "batch") await apiClient.deleteBatchJob(session.id);
      else await apiClient.deleteConversation(session.id);
      setOverview((prev) =>
        prev
          ? { ...prev, recentSessions: prev.recentSessions.filter((s) => s.id !== session.id) }
          : prev,
      );
    } catch { /* ignore */ }
    setConfirmDeleteId(null);
  }

  function handleSessionClick(session: RecentSessionItem) {
    if (session.type === "batch" && session.status === "done") {
      onViewBatch(session.id);
    } else if (session.type === "form" && session.status === "done") {
      onSelectStudent(session.id);
    } else if (session.type === "chat" && session.status === "done") {
      onSelectStudent(session.id);
    } else if (session.type === "chat" && session.status === "in_progress") {
      onContinueChat(session.id);
    }
  }

  const isSessionClickable = (_s: RecentSessionItem) => true;


  return (
    <div className="dashboard">
      <div className="dashboard__stats">
        <button type="button" className="stat-card stat-card--clickable" onClick={onViewAllSessions}>
          <div className="stat-card__label">Total assessed</div>
          <div className="stat-card__value">{overview?.totalAssessed ?? "—"}</div>
        </button>
        <button type="button" className="stat-card stat-card--clickable" onClick={() => onViewAllStudents("low")}>
          <div className="stat-card__label-row">
            <span className="risk-dot risk-dot--low" />
            <span className="stat-card__label">Low risk</span>
          </div>
          <div className="stat-card__value stat-card__value--low">{overview?.lowRisk ?? "—"}</div>
        </button>
        <button type="button" className="stat-card stat-card--clickable" onClick={() => onViewAllStudents("medium")}>
          <div className="stat-card__label-row">
            <span className="risk-dot risk-dot--medium" />
            <span className="stat-card__label">Medium risk</span>
          </div>
          <div className="stat-card__value stat-card__value--medium">{overview?.mediumRisk ?? "—"}</div>
        </button>
        <button type="button" className="stat-card stat-card--clickable" onClick={() => onViewAllStudents("high")}>
          <div className="stat-card__label-row">
            <span className="risk-dot risk-dot--high" />
            <span className="stat-card__label">High risk</span>
          </div>
          <div className="stat-card__value stat-card__value--high">{overview?.highRisk ?? "—"}</div>
        </button>
      </div>

      <div className="dashboard__actions-row">
        <button type="button" className="action-btn" onClick={onStartChat}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
          </svg>
          New chat assessment
        </button>
        <button type="button" className="action-btn" onClick={onStartUpload}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 3v12m0-12 4 4m-4-4-4 4" />
            <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
          </svg>
          Upload batch file
        </button>
      </div>

      <div className="dashboard__main">
        <div className="panel">
          <div className="panel__title">Recent sessions</div>
          {error && <div className="activity-error">{error}</div>}
          {!error && !overview && <div className="activity-loading">Loading…</div>}
          {overview && overview.recentSessions.length === 0 && (
            <div className="activity-empty">No sessions yet.</div>
          )}
          <div className="session-list">
            {overview?.recentSessions.map((session) => (
              <div key={session.id} className="session-row">
                <div
                  className="session-row__clickarea"
                  onClick={() => handleSessionClick(session)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === "Enter" && handleSessionClick(session)}
                >
                  <div className={`session-row__icon session-row__icon--${session.type}`}>
                    <SessionIcon type={session.type} />
                  </div>
                  <div className="session-row__body">
                    <div className="session-row__label">{session.label}</div>
                    <div className="session-row__meta">
                      {timeAgo(session.createdAt)}
                      {session.type === "batch" && session.studentCount != null && (
                        <> · {session.studentCount} student{session.studentCount === 1 ? "" : "s"}</>
                      )}
                    </div>
                  </div>
                  <div className="session-row__right">
                    {session.type !== "batch" && session.status === "done" && session.riskLevel ? (
                      <RiskBadge level={session.riskLevel} />
                    ) : (
                      <StatusChip status={session.status} />
                    )}
                  </div>
                </div>
                <div className="session-row__actions">
                  {confirmDeleteId === session.id ? (
                    <div className="session-delete-confirm">
                      <span className="session-delete-confirm__label">Delete?</span>
                      <button type="button" className="session-delete-confirm__yes" onClick={() => deleteSession(session)}>Yes</button>
                      <button type="button" className="session-delete-confirm__no" onClick={() => setConfirmDeleteId(null)}>No</button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      className="session-delete-btn"
                      title="Delete"
                      onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(session.id); }}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14H6L5 6" />
                        <path d="M10 11v6M14 11v6" />
                        <path d="M9 6V4h6v2" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          {overview && overview.recentSessions.length > 0 && (
            <button type="button" className="session-view-all" onClick={onViewAllSessions}>
              View all sessions →
            </button>
          )}
        </div>

        <div className="panel">
          <div className="panel__title">Recent students</div>
          {overview && overview.recentStudents.length === 0 && (
            <div className="activity-empty">No assessments yet.</div>
          )}
          <div className="activity-list">
            {overview?.recentStudents.map((item) => (
              <div
                className="activity-row activity-row--clickable"
                key={item.id}
                onClick={() => onSelectStudent(item.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === "Enter" && onSelectStudent(item.id)}
              >
                <div className="activity-row__info">
                  <div className="avatar">{initialsOf(item.name)}</div>
                  <div>
                    <div className="activity-row__name">{item.name}</div>
                    <div className="activity-row__meta">
                      {timeAgo(item.assessedAt)} · {item.statusLabel}
                    </div>
                  </div>
                </div>
                <RiskBadge level={item.riskLevel} />
              </div>
            ))}
          </div>
          {overview && overview.recentStudents.length > 0 && (
            <button type="button" className="session-view-all" onClick={onViewAllStudents}>
              View all students →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
