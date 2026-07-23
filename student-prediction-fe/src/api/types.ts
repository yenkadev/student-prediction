import type { AcademicFeatures, DataSource, PredictionType, RiskAssessment, RiskLevel, PredictedStatus, Student } from "../types";

/**
 * Contract mirrors the proposed BE Service API (see
 * uploads/context_thiet_ke_application_layer.md, section 5.1):
 *   POST /predict/chat  — sync, one student per turn
 *   POST /predict/batch — async, returns a job_id to poll
 *   GET  /predict/batch/{job_id} — poll job status
 */

export interface ChatRequest {
  message: string;
  conversationId?: string;
  dataSource: DataSource;
  predictionType: PredictionType;
}

export interface ChatNeedMoreInfoResponse {
  type: "need_more_info";
  conversationId: string;
  question: string;
}

export interface ChatResultResponse {
  type: "result";
  conversationId: string;
  data: RiskAssessment;
}

export type ChatResponse = ChatNeedMoreInfoResponse | ChatResultResponse;

export interface BatchSubmitResponse {
  jobId: string;
}

export interface AssessmentOptions {
  dataSource: DataSource;
  predictionType: PredictionType;
}

export interface BatchSyncResponse {
  results: Student[];
}

export type BatchJobStatus = "processing" | "done" | "failed";

export interface BatchJobResponse {
  status: BatchJobStatus;
  progress: number;
  results?: Student[];
  error?: string;
}

export interface OverviewActivityItem {
  id: string;
  name: string;
  studentId: string;
  statusLabel: PredictedStatus;
  riskLevel: RiskLevel;
  assessedAt: string; // ISO-8601
}

export type SessionStatus = "in_progress" | "done" | "failed";

export interface RecentSessionItem {
  id: string;
  type: "chat" | "batch";
  label: string;
  createdAt: string;
  status: SessionStatus;
  studentCount?: number;
  riskLevel?: RiskLevel;
}

export interface OverviewResponse {
  totalAssessed: number;
  lowRisk: number;
  mediumRisk: number;
  highRisk: number;
  recentSessions: RecentSessionItem[];
  recentStudents: OverviewActivityItem[];
}

export interface StudentDetailResponse {
  id: string;
  name: string;
  studentId: string;
  source: "batch" | "chat";
  reviewed: boolean;
  assessed_at: string;
  assessment: RiskAssessment;
  features?: AcademicFeatures | null;
}

export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}

export interface ConversationDetail {
  id: string;
  dataSource?: DataSource;
  predictionType?: PredictionType;
  turns: ConversationTurn[];
  fields: Record<string, unknown>;
  assessment?: RiskAssessment;
  assessed_at?: string;
  created_at: string;
}

export interface AllSessionsResponse {
  sessions: RecentSessionItem[];
}

export interface AllStudentsResponse {
  students: OverviewActivityItem[];
}

export interface RiskWarningApiClient {
  predictChat(request: ChatRequest): Promise<ChatResponse>;
  submitBatch(file: File, options: AssessmentOptions): Promise<BatchSyncResponse>;
  getBatchJob(jobId: string): Promise<BatchJobResponse>;
  getOverview(): Promise<OverviewResponse>;
  getStudent(id: string): Promise<StudentDetailResponse>;
  getConversation(id: string): Promise<ConversationDetail>;
  getAllSessions(): Promise<AllSessionsResponse>;
  getAllStudents(): Promise<AllStudentsResponse>;
  deleteConversation(id: string): Promise<void>;
  deleteBatchJob(jobId: string): Promise<void>;
}
