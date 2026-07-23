import { useState } from "react";
import type { ConversationTurn } from "../api/types";
import type { DataSource, PredictionType, RiskAssessment, Student } from "../types";
import { ChatPanel } from "./ChatPanel";
import { UploadPanel } from "./UploadPanel";
import "./NewAssessment.css";

type InputMode = "chat" | "upload";

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
  const [dataSource, setDataSource] = useState<DataSource>("student_dropout");
  const [predictionType, setPredictionType] = useState<PredictionType>("ml");

  return (
    <div className="new-assessment">
      <div className="assessment-config" aria-label="Assessment configuration">
        <label className="assessment-config__field">
          <span>Nguồn dữ liệu</span>
          <select
            value={dataSource}
            onChange={(event) => setDataSource(event.target.value as DataSource)}
            data-testid="data-source-select"
          >
            <option value="student_dropout">student_dropout.csv — hành vi học tập</option>
            <option value="student_dropout_and_success">student_dropout_and_success.csv — học vụ</option>
          </select>
        </label>
        <label className="assessment-config__field">
          <span>Giải pháp</span>
          <select
            value={predictionType}
            onChange={(event) => setPredictionType(event.target.value as PredictionType)}
            data-testid="prediction-type-select"
          >
            <option value="ml">Machine Learning</option>
            <option value="rule_based">Rule-based Scoring</option>
          </select>
        </label>
        <div className="assessment-config__summary" data-testid="assessment-summary">
          Đang dùng <strong>{dataSource}.csv</strong> với{" "}
          <strong>{predictionType === "ml" ? "Machine Learning" : "Rule-based Scoring"}</strong>
        </div>
      </div>
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
          className={`mode-toggle__btn${mode === "upload" ? " mode-toggle__btn--active" : ""}`}
          onClick={() => setMode("upload")}
        >
          Upload file
        </button>
      </div>

      {mode === "chat" ? (
        <ChatPanel
          key={`${dataSource}-${predictionType}`}
          dataSource={dataSource}
          predictionType={predictionType}
          resumeConversationId={resumeConversationId}
          resumeTurns={resumeTurns}
          resumeAssessment={resumeAssessment}
        />
      ) : (
        <UploadPanel
          dataSource={dataSource}
          predictionType={predictionType}
          onBatchComplete={onBatchComplete}
        />
      )}
    </div>
  );
}
