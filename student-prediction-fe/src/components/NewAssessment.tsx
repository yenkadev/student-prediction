import { useState } from "react";
import type { ConversationTurn } from "../api/types";
import type { DataSource, PredictionType, RiskAssessment, Student } from "../types";
import { useDevSettings } from "../devSettings";
import { ChatPanel } from "./ChatPanel";
import { FormPanel } from "./FormPanel";
import { UploadPanel } from "./UploadPanel";
import "./NewAssessment.css";

const DATA_SOURCE_LABELS: Record<DataSource, string> = {
  student_dropout: "student_dropout.csv — study behaviour",
  student_dropout_and_success: "student_dropout_and_success.csv — academic record",
};

const SOLUTION_LABELS: Record<PredictionType, string> = {
  ml: "Machine Learning",
  rule_based: "Rule-based Scoring",
};

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
  const { settings } = useDevSettings();
  const [mode, setMode] = useState<InputMode>(initialMode);
  const [dataSource, setDataSource] = useState<DataSource>("student_dropout");
  const [predictionType, setPredictionType] = useState<PredictionType>("ml");

  return (
    <div className="new-assessment">
      {settings.experimentControls && (
        <div className="assessment-config" aria-label="Experiment configuration">
          <div className="assessment-config__header">
            <span className="assessment-config__badge">Dev</span>
            <span className="assessment-config__title">Experiment controls</span>
          </div>
          <label className="assessment-config__field">
            <span>Data source</span>
            <select
              value={dataSource}
              onChange={(event) => setDataSource(event.target.value as DataSource)}
              data-testid="data-source-select"
            >
              {(Object.keys(DATA_SOURCE_LABELS) as DataSource[]).map((value) => (
                <option value={value} key={value}>
                  {DATA_SOURCE_LABELS[value]}
                </option>
              ))}
            </select>
          </label>
          <label className="assessment-config__field">
            <span>Solution</span>
            <select
              value={predictionType}
              onChange={(event) => setPredictionType(event.target.value as PredictionType)}
              data-testid="prediction-type-select"
            >
              {(Object.keys(SOLUTION_LABELS) as PredictionType[]).map((value) => (
                <option value={value} key={value}>
                  {SOLUTION_LABELS[value]}
                </option>
              ))}
            </select>
          </label>
          <div className="assessment-config__summary" data-testid="assessment-summary">
            Using <strong>{dataSource}.csv</strong> with <strong>{SOLUTION_LABELS[predictionType]}</strong>
          </div>
        </div>
      )}
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
          key={`${dataSource}-${predictionType}`}
          dataSource={dataSource}
          predictionType={predictionType}
          resumeConversationId={resumeConversationId}
          resumeTurns={resumeTurns}
          resumeAssessment={resumeAssessment}
        />
      ) : mode === "form" ? (
        <FormPanel dataSource={dataSource} predictionType={predictionType} />
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
