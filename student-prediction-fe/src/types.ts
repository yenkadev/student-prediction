export type RiskLevel = "low" | "medium" | "high";

export interface AcademicFeatures {
  GPA?: number | null;
  Attendance_Rate?: number | null;
  Stress_Index?: number | null;
  Study_Hours_per_Day?: number | null;
  Assignment_Delay_Days?: number | null;
  Internet_Access?: string | null;
  Part_Time_Job?: string | null;
  Gender?: string | null;
  Scholarship?: string | null;
  Semester?: string | null;
  Department?: string | null;
  Parental_Education?: string | null;
  Age?: number | null;
  Family_Income?: number | null;
  Travel_Time_Minutes?: number | null;
  Semester_GPA?: number | null;
  CGPA?: number | null;
}

export type PredictedStatus = "Dropout" | "Enrolled" | "Graduate";

export interface RiskAssessment {
  statusLabel: PredictedStatus;
  riskLevel: RiskLevel;
  riskProb: number;
  recommendation: string;
  factors: string[];
}

export interface Student {
  id: string;
  name: string;
  studentId: string;
  reviewed?: boolean;
  assessment: RiskAssessment;
}

export function riskLevelFromProb(prob: number): RiskLevel {
  if (prob > 0.6) return "high";
  if (prob >= 0.3) return "medium";
  return "low";
}

export function initialsOf(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}
