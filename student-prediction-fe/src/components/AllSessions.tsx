import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { RecentSessionItem } from "../api/types";
import { RiskBadge } from "./RiskBadge";
import "./AllSessions.css";

interface AllSessionsProps {
  onSelectStudent: (id: string) => void;
  onViewBatch: (jobId: string) => void;
  onContinueChat: (conversationId: string) => void;
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

function SessionIcon({ type }: { type: "chat" | "batch" }) {
  if (type === "batch") {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
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
    <span className={`as-status-chip as-status-chip--${status}`}>
      {status === "done" ? "Done" : status === "in_progress" ? "In progress" : "Failed"}
    </span>
  );
}

function TrashIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4h6v2" />
    </svg>
  );
}

export function AllSessions({ onSelectStudent, onViewBatch, onContinueChat }: AllSessionsProps) {
  const [sessions, setSessions] = useState<RecentSessionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  useEffect(() => {
    apiClient.getAllSessions()
      .then((res) => { setSessions(res.sessions); setLoading(false); })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load sessions");
        setLoading(false);
      });
  }, []);

  function handleClick(session: RecentSessionItem) {
    if (session.type === "batch" && session.status === "done") onViewBatch(session.id);
    else if (session.type === "chat" && session.status === "done") onSelectStudent(session.id);
    else if (session.type === "chat" && session.status === "in_progress") onContinueChat(session.id);
  }

  async function handleDelete(session: RecentSessionItem) {
    try {
      if (session.type === "chat") {
        await apiClient.deleteConversation(session.id);
      } else {
        await apiClient.deleteBatchJob(session.id);
      }
      setSessions((prev) => prev.filter((s) => s.id !== session.id));
    } catch {
      // silently ignore
    }
    setConfirmDeleteId(null);
  }

  if (loading) return <div className="as-empty">Loading…</div>;
  if (error) return <div className="as-error">{error}</div>;
  if (sessions.length === 0) return <div className="as-empty">No sessions yet.</div>;

  return (
    <div className="as-list">
      {sessions.map((session) => (
        <div key={session.id} className="as-row">
          <div
            className="as-row__main"
            onClick={() => handleClick(session)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && handleClick(session)}
          >
            <div className={`as-row__icon as-row__icon--${session.type}`}>
              <SessionIcon type={session.type} />
            </div>
            <div className="as-row__body">
              <div className="as-row__label">{session.label}</div>
              <div className="as-row__meta">
                {timeAgo(session.createdAt)}
                {session.type === "batch" && session.studentCount != null && (
                  <> · {session.studentCount} student{session.studentCount === 1 ? "" : "s"}</>
                )}
              </div>
            </div>
            <div className="as-row__badge">
              {session.type === "chat" && session.status === "done" && session.riskLevel ? (
                <RiskBadge level={session.riskLevel} />
              ) : (
                <StatusChip status={session.status} />
              )}
            </div>
          </div>

          <div className="as-row__actions">
            {confirmDeleteId === session.id ? (
              <div className="as-confirm">
                <span className="as-confirm__label">Delete?</span>
                <button type="button" className="as-confirm__yes" onClick={() => handleDelete(session)}>Yes</button>
                <button type="button" className="as-confirm__no" onClick={() => setConfirmDeleteId(null)}>No</button>
              </div>
            ) : (
              <button
                type="button"
                className="as-delete-btn"
                title="Delete"
                onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(session.id); }}
              >
                <TrashIcon />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
