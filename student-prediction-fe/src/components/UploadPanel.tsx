import { useRef, useState } from "react";
import { apiClient } from "../api/client";
import type { DataSource, PredictionType, Student } from "../types";
import "./UploadPanel.css";

interface UploadedFile {
  name: string;
  sizeKB: number;
}

interface UploadPanelProps {
  dataSource: DataSource;
  predictionType: PredictionType;
  onBatchComplete: (students: Student[]) => void;
}

export function UploadPanel({ dataSource, predictionType, onBatchComplete }: UploadPanelProps) {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const selectedFileRef = useRef<File | null>(null);

  function selectFile(file: File) {
    if (!/\.(csv|xlsx|xls)$/i.test(file.name)) {
      selectedFileRef.current = null;
      setUploadedFile(null);
      setError("File phải có định dạng CSV hoặc Excel (.csv, .xlsx, .xls).");
      return;
    }
    selectedFileRef.current = file;
    const sizeKB = Math.max(1, Math.round(file.size / 1024));
    setError(null);
    setUploadedFile({ name: file.name, sizeKB });
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) selectFile(file);
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) selectFile(file);
  }

  function removeFile() {
    setUploadedFile(null);
    selectedFileRef.current = null;
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function startBatchAnalysis() {
    if (!uploadedFile || !selectedFileRef.current) return;
    setIsProcessing(true);
    setProgress(25);
    setError(null);

    try {
      const response = await apiClient.submitBatch(selectedFileRef.current, {
        dataSource,
        predictionType,
      });
      setProgress(100);
      setUploadedFile(null);
      selectedFileRef.current = null;
      onBatchComplete(response.results);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Không thể phân tích file.");
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  }

  return (
    <div className="upload-panel">
      {isProcessing ? (
        <div className="upload-processing">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#B8892B" strokeWidth="2" className="spin-icon">
            <path d="M21 12a9 9 0 1 1-2.6-6.36" />
          </svg>
          <div className="upload-processing__title">Processing batch job…</div>
          <div className="upload-processing__desc">
            Đang chạy {predictionType === "ml" ? "Machine Learning" : "Rule-based Scoring"} trên {dataSource}.csv
          </div>
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
              <div className="uploaded-file__meta">{uploadedFile.sizeKB} KB · Cấu trúc cột sẽ được backend kiểm tra</div>
            </div>
            <button type="button" className="uploaded-file__remove" onClick={removeFile}>
              Remove
            </button>
          </div>
          <button type="button" className="upload-start-btn" onClick={startBatchAnalysis}>
            Phân tích bằng {predictionType === "ml" ? "Machine Learning" : "Rule-based Scoring"}
          </button>
          {error && <div className="upload-error" role="alert">{error}</div>}
        </div>
      ) : (
        <div>
          <div
            className={`dropzone${isDragging ? " dropzone--dragging" : ""}`}
            role="button"
            tabIndex={0}
            aria-label="Chọn hoặc kéo thả file CSV, Excel"
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") fileInputRef.current?.click();
            }}
            onDragEnter={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#B8892B" strokeWidth="1.8">
              <path d="M12 3v12m0-12 4 4m-4-4-4 4" />
              <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
            </svg>
            <div className="dropzone__title">Kéo thả file CSV hoặc Excel vào đây</div>
            <div className="dropzone__desc">hoặc nhấn để chọn file · .csv, .xlsx, .xls</div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
          <div className="upload-hint">
            Hãy dùng đúng cấu trúc cột của {dataSource}.csv. File Excel cần đặt dữ liệu ở sheet đầu tiên.
          </div>
          {error && <div className="upload-error" role="alert">{error}</div>}
        </div>
      )}
    </div>
  );
}
