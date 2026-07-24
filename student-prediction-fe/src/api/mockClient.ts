import { MOCK_STUDENTS } from "./mockData";
import type {
  AssessmentOptions,
  BatchJobResponse,
  BatchSyncResponse,
  ChatRequest,
  ChatResponse,
  FormRequest,
  FormResultResponse,
  StudentDetailResponse,
} from "./types";

function delay<T>(value: T, ms: number): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

let conversationCounter = 0;

interface JobState {
  progress: number;
  status: "processing" | "done";
}

const jobs = new Map<string, JobState>();

export class MockRiskWarningApiClient {
  async predictChat(request: ChatRequest): Promise<ChatResponse> {
    const conversationId = request.conversationId ?? `conv-${++conversationCounter}`;
    const isFirstTurn = !request.conversationId;

    if (isFirstTurn) {
      return delay<ChatResponse>(
        {
          type: "need_more_info",
          conversationId,
          question:
            "Thanks — a couple more details would help: has tuition been paid up to date, and about how many classes has the student missed this term?",
        },
        1100,
      );
    }

    return delay<ChatResponse>(
      {
        type: "result",
        conversationId,
        data: {
          dataSource: request.dataSource,
          solutionType: request.predictionType,
          prediction: "Dropout",
          riskScore: 0.74,
          statusLabel: "Dropout",
          riskLevel: "high",
          riskProb: 0.74,
          scoreType: request.predictionType === "ml" ? "probability" : "normalized_rule_score",
          recommendations: ["Financial aid outreach", "Personal counseling"],
          riskFactors: [
            "Tuition fees overdue by 2 installments",
            "Failed 2 of 5 courses this term",
            "Attendance around 70% — missed multiple classes",
          ],
          recommendation: "Financial aid outreach, Personal counseling",
          factors: [
            "Tuition fees overdue by 2 installments",
            "Failed 2 of 5 courses this term",
            "Attendance around 70% — missed multiple classes",
          ],
        },
      },
      1400,
    );
  }

  async predictForm(request: FormRequest): Promise<FormResultResponse> {
    const high = Number(request.fields.GPA ?? 4) < 2 || Number(request.fields.Attendance_Rate ?? 100) < 70;
    return delay<FormResultResponse>(
      {
        conversationId: `conv-${++conversationCounter}`,
        data: high
          ? {
              dataSource: request.dataSource,
              solutionType: request.predictionType,
              prediction: "Dropout",
              riskScore: 0.71,
              statusLabel: "Dropout",
              riskLevel: "high",
              riskProb: 0.71,
              scoreType: request.predictionType === "ml" ? "probability" : "normalized_rule_score",
              recommendations: [
                "Immediate intervention required",
                "Connect student with academic advisor and counseling services",
              ],
              riskFactors: ["GPA", "Attendance_Rate", "Study_Hours_per_Day"],
              recommendation:
                "Immediate intervention required. Connect student with academic advisor and counseling services.",
              factors: ["GPA", "Attendance_Rate", "Study_Hours_per_Day"],
            }
          : {
              dataSource: request.dataSource,
              solutionType: request.predictionType,
              prediction: "No Dropout",
              riskScore: 0.18,
              statusLabel: "Graduate",
              riskLevel: "low",
              riskProb: 0.18,
              scoreType: request.predictionType === "ml" ? "probability" : "normalized_rule_score",
              recommendations: ["Student is on track", "Continue regular academic monitoring"],
              riskFactors: ["GPA", "Attendance_Rate", "Stress_Index"],
              recommendation: "Student is on track. Continue regular academic monitoring.",
              factors: ["GPA", "Attendance_Rate", "Stress_Index"],
            },
      },
      900,
    );
  }

  async submitBatch(_file: File, _options: AssessmentOptions): Promise<BatchSyncResponse> {
    return delay({ results: MOCK_STUDENTS }, 300);
  }

  async getBatchJob(jobId: string): Promise<BatchJobResponse> {
    const job = jobs.get(jobId);
    if (!job) {
      return { status: "failed", progress: 0, error: "Job not found" };
    }

    if (job.status === "processing") {
      job.progress = Math.min(100, job.progress + 8 + Math.random() * 10);
      if (job.progress >= 100) {
        job.status = "done";
        return delay({ status: "done", progress: 100, results: MOCK_STUDENTS }, 150);
      }
      return delay({ status: "processing", progress: job.progress }, 220);
    }

    return { status: "done", progress: 100, results: MOCK_STUDENTS };
  }

  async getStudent(id: string): Promise<StudentDetailResponse> {
    const found = MOCK_STUDENTS.find((s) => s.id === id);
    if (!found) throw new Error(`Student ${id} not found`);
    return delay<StudentDetailResponse>(
      {
        ...found,
        reviewed: found.reviewed ?? false,
        source: "batch",
        assessed_at: new Date(Date.now() - 3600_000).toISOString(),
        features: {
          GPA: 2.4,
          Attendance_Rate: 61,
          Stress_Index: 8,
          Study_Hours_per_Day: 2,
          Assignment_Delay_Days: 5,
          Internet_Access: "Yes",
          Part_Time_Job: "Yes",
        },
      },
      400,
    );
  }
}
