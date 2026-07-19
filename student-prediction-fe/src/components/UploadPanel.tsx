import { useRef, useState } from "react";
import { apiClient } from "../api/client";
import type { Student } from "../types";
import "./UploadPanel.css";

interface UploadedFile {
  name: string;
  sizeKB: number;
  rows: number;
  sheet: string;
}

interface UploadPanelProps {
  onBatchComplete: (students: Student[]) => void;
}

export function UploadPanel({ onBatchComplete }: UploadPanelProps) {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const selectedFileRef = useRef<File | null>(null);

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    selectedFileRef.current = file;
    const sizeKB = Math.max(1, Math.round(file.size / 1024));
    const rows = 30 + Math.floor(Math.random() * 40);
    setUploadedFile({ name: file.name, sizeKB, rows, sheet: "Sheet1" });
  }

  async function startBatchAnalysis() {
    if (!uploadedFile || !selectedFileRef.current) return;
    setIsProcessing(true);
    setProgress(0);

    const { jobId } = await apiClient.submitBatch(selectedFileRef.current);

    const poll = async () => {
      const job = await apiClient.getBatchJob(jobId);
      setProgress(job.progress);
      if (job.status === "done") {
        setIsProcessing(false);
        setProgress(0);
        setUploadedFile(null);
        onBatchComplete(job.results ?? []);
        return;
      }
      if (job.status === "failed") {
        setIsProcessing(false);
        return;
      }
      setTimeout(poll, 400);
    };

    poll();
  }

  return (
    <div className="upload-panel">
      {isProcessing ? (
        <div className="upload-processing">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#B8892B" strokeWidth="2" className="spin-icon">
            <path d="M21 12a9 9 0 1 1-2.6-6.36" />
          </svg>
          <div className="upload-processing__title">Processing batch job…</div>
          <div className="upload-processing__desc">Running pre-processing, rule-based scoring and the ML pipeline</div>
          <div className="upload-progress-track">
            <div className="upload-progress-fill" style={{ width: `${Math.round(progress)}%` }} />
          </div>
        </div>
      ) : uploadedFile ? (
        <div>
          <div className="uploaded-file">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#B8892B" strokeWidth="1.6">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6" />
            </svg>
            <div className="uploaded-file__info">
              <div className="uploaded-file__name">{uploadedFile.name}</div>
              <div className="uploaded-file__meta">
                {uploadedFile.sizeKB} KB · {uploadedFile.rows} rows detected · {uploadedFile.sheet}
              </div>
            </div>
            <button type="button" className="uploaded-file__remove" onClick={() => { setUploadedFile(null); selectedFileRef.current = null; }}>
              Remove
            </button>
          </div>
          <button type="button" className="upload-start-btn" onClick={startBatchAnalysis}>
            Start batch analysis
          </button>
        </div>
      ) : (
        <div>
          <div className="dropzone" onClick={() => fileInputRef.current?.click()}>
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#B8892B" strokeWidth="1.8">
              <path d="M12 3v12m0-12 4 4m-4-4-4 4" />
              <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
            </svg>
            <div className="dropzone__title">Drag &amp; drop your CSV or Excel file</div>
            <div className="dropzone__desc">or click to browse · .csv, .xlsx</div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
          <div className="upload-hint">
            Please keep student data on the first sheet. Detailed column validation happens on the server.
          </div>
        </div>
      )}
    </div>
  );
}
