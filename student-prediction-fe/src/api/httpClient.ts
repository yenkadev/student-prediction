import type {
  AllSessionsResponse,
  AllStudentsResponse,
  BatchJobResponse,
  BatchSubmitResponse,
  ChatRequest,
  ChatResponse,
  ConversationDetail,
  OverviewResponse,
  RiskWarningApiClient,
  StudentDetailResponse,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

// predictionType is required by the BE but not yet part of the FE ChatRequest type.
// Defaulting to "ml" here; change to "rule_based" or surface it in the UI later.
const DEFAULT_PREDICTION_TYPE = "ml";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export class HttpRiskWarningApiClient implements RiskWarningApiClient {
  async predictChat(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${BASE_URL}/predict/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: request.message,
        conversationId: request.conversationId,
        predictionType: DEFAULT_PREDICTION_TYPE,
      }),
    });
    return handleResponse<ChatResponse>(res);
  }

  async submitBatch(file: File): Promise<BatchSubmitResponse> {
    const form = new FormData();
    form.append("file", file);
    form.append("predictionType", DEFAULT_PREDICTION_TYPE);

    const res = await fetch(`${BASE_URL}/predict/batch`, {
      method: "POST",
      body: form,
    });
    return handleResponse<BatchSubmitResponse>(res);
  }

  async getBatchJob(jobId: string): Promise<BatchJobResponse> {
    const res = await fetch(`${BASE_URL}/predict/batch/${jobId}`);
    return handleResponse<BatchJobResponse>(res);
  }

  async getOverview(): Promise<OverviewResponse> {
    const res = await fetch(`${BASE_URL}/overview`);
    return handleResponse<OverviewResponse>(res);
  }

  async getStudent(id: string): Promise<StudentDetailResponse> {
    const res = await fetch(`${BASE_URL}/students/${id}`);
    return handleResponse<StudentDetailResponse>(res);
  }

  async getConversation(id: string): Promise<ConversationDetail> {
    const res = await fetch(`${BASE_URL}/conversations/${id}`);
    return handleResponse<ConversationDetail>(res);
  }

  async getAllSessions(): Promise<AllSessionsResponse> {
    const res = await fetch(`${BASE_URL}/sessions`);
    return handleResponse<AllSessionsResponse>(res);
  }

  async getAllStudents(): Promise<AllStudentsResponse> {
    const res = await fetch(`${BASE_URL}/students`);
    return handleResponse<AllStudentsResponse>(res);
  }

  async deleteConversation(id: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/conversations/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  }

  async deleteBatchJob(jobId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/predict/batch/${jobId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  }
}
