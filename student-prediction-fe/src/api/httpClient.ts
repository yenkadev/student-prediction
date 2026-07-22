import type {
  AllSessionsResponse,
  AllStudentsResponse,
  AssessmentOptions,
  BatchJobResponse,
  BatchSyncResponse,
  ChatRequest,
  ChatResponse,
  ConversationDetail,
  OverviewResponse,
  RiskWarningApiClient,
  StudentDetailResponse,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = res.statusText || `Yêu cầu thất bại với mã ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Giữ thông báo HTTP mặc định nếu response không phải JSON.
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

async function requestApi(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch {
    throw new Error("Không thể kết nối backend. Hãy kiểm tra API tại http://127.0.0.1:8000/health.");
  }
}

export class HttpRiskWarningApiClient implements RiskWarningApiClient {
  async predictChat(request: ChatRequest): Promise<ChatResponse> {
    const res = await requestApi(`${BASE_URL}/predict/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: request.message,
        conversationId: request.conversationId,
        dataSource: request.dataSource,
        predictionType: request.predictionType,
      }),
    });
    return handleResponse<ChatResponse>(res);
  }

  async submitBatch(file: File, options: AssessmentOptions): Promise<BatchSyncResponse> {
    const form = new FormData();
    form.append("file", file);
    form.append("dataSource", options.dataSource);
    form.append("predictionType", options.predictionType);

    const res = await requestApi(`${BASE_URL}/predict/batch/sync`, {
      method: "POST",
      body: form,
    });
    return handleResponse<BatchSyncResponse>(res);
  }

  async getBatchJob(jobId: string): Promise<BatchJobResponse> {
    const res = await requestApi(`${BASE_URL}/predict/batch/${jobId}`);
    return handleResponse<BatchJobResponse>(res);
  }

  async getOverview(): Promise<OverviewResponse> {
    const res = await requestApi(`${BASE_URL}/overview`);
    return handleResponse<OverviewResponse>(res);
  }

  async getStudent(id: string): Promise<StudentDetailResponse> {
    const res = await requestApi(`${BASE_URL}/students/${id}`);
    return handleResponse<StudentDetailResponse>(res);
  }

  async getConversation(id: string): Promise<ConversationDetail> {
    const res = await requestApi(`${BASE_URL}/conversations/${id}`);
    return handleResponse<ConversationDetail>(res);
  }

  async getAllSessions(): Promise<AllSessionsResponse> {
    const res = await requestApi(`${BASE_URL}/sessions`);
    return handleResponse<AllSessionsResponse>(res);
  }

  async getAllStudents(): Promise<AllStudentsResponse> {
    const res = await requestApi(`${BASE_URL}/students`);
    return handleResponse<AllStudentsResponse>(res);
  }

  async deleteConversation(id: string): Promise<void> {
    const res = await requestApi(`${BASE_URL}/conversations/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  }

  async deleteBatchJob(jobId: string): Promise<void> {
    const res = await requestApi(`${BASE_URL}/predict/batch/${jobId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  }
}
