import { useState } from "react";
import type { ConversationTurn } from "../api/types";
import type { RiskAssessment, Student } from "../types";
import { ChatPanel } from "./ChatPanel";
import { FormPanel } from "./FormPanel";
import { UploadPanel } from "./UploadPanel";
import "./NewAssessment.css";

type InputMode = "chat" | "form" | "upload";

interface NewAssessmentProps {
  initialMode: InputMode;
  onBatchComplete: (students: Student[]) => void;
  resumeConversationId?: string;
  resumeTurns?: ConversationTurn[];
  resumeAssessment?: RiskAssessment;
}

export function NewAssessment({
  initialMode,
  onBatchComplete,
  resumeConversationId,
  resumeTurns,
  resumeAssessment,
}: NewAssessmentProps) {
  const [mode, setMode] = useState<InputMode>(initialMode);

  return (
    <div className="new-assessment">
      <div className="mode-toggle">
        <button
          type="button"
          className={`mode-toggle__btn${mode === "chat" ? " mode-toggle__btn--active" : ""}`}
          onClick={() => setMode("chat")}
        >
          Chat
        </button>
        <button
          type="button"
          className={`mode-toggle__btn${mode === "form" ? " mode-toggle__btn--active" : ""}`}
          onClick={() => setMode("form")}
        >
          Form
        </button>
        <button
          type="button"
          className={`mode-toggle__btn${mode === "upload" ? " mode-toggle__btn--active" : ""}`}
          onClick={() => setMode("upload")}
        >
          Upload file
        </button>
      </div>

      {mode === "chat" ? (
        <ChatPanel
          resumeConversationId={resumeConversationId}
          resumeTurns={resumeTurns}
          resumeAssessment={resumeAssessment}
        />
      ) : mode === "form" ? (
        <FormPanel />
      ) : (
        <UploadPanel onBatchComplete={onBatchComplete} />
      )}
    </div>
  );
}
