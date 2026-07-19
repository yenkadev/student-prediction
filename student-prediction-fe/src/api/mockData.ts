import { riskLevelFromProb, type Student } from "../types";

function student(
  id: string,
  name: string,
  studentId: string,
  status: Student["assessment"]["statusLabel"],
  riskProb: number,
  recommendation: string,
  factors: string[],
): Student {
  return {
    id,
    name,
    studentId,
    assessment: {
      statusLabel: status,
      riskLevel: riskLevelFromProb(riskProb),
      riskProb,
      recommendation,
      factors,
    },
  };
}

export const MOCK_STUDENTS: Student[] = [
  student("s1", "Marcus Bell", "STU-10231", "Dropout", 0.81, "Financial aid outreach, Personal counseling", [
    "Tuition fees overdue by 2 installments",
    "Failed 3 of 5 courses in Term 1",
    "Attendance around 61% (14 absences)",
  ]),
  student("s2", "Priya Nair", "STU-10232", "Graduate", 0.08, "Routine academic monitoring", [
    "All courses passed this term",
    "Tuition payments up to date",
    "Attendance rate 96%",
  ]),
  student("s3", "Diego Alvarez", "STU-10233", "Enrolled", 0.42, "Academic support", [
    "Failed 1 of 6 courses",
    "Low weekly study time (2 hrs)",
    "Attendance rate 84%",
  ]),
  student("s4", "Chloe Nakamura", "STU-10234", "Dropout", 0.77, "Financial aid outreach", [
    "Tuition overdue, scholarship revoked",
    "Failed 2 of 4 courses",
    "Declining engagement since midterm",
  ]),
  student("s5", "Samuel Osei", "STU-10235", "Enrolled", 0.35, "Personal counseling", [
    "Attendance dipped to 79% this term",
    "First-semester international student",
    "No failed courses yet",
  ]),
  student("s6", "Elena Petrova", "STU-10236", "Graduate", 0.12, "Routine academic monitoring", [
    "Strong pass rate across all terms",
    "Tuition up to date",
    "Consistent attendance",
  ]),
  student("s7", "Tyler Brooks", "STU-10237", "Dropout", 0.69, "Academic support, Personal counseling", [
    "Failed 3 of 5 courses",
    "22 absences this term",
    "No family academic support on file",
  ]),
  student("s8", "Amara Diallo", "STU-10238", "Enrolled", 0.5, "Financial aid outreach", [
    "Tuition installment overdue",
    "Low weekly study time",
    "Attendance rate 82%",
  ]),
  student("s9", "Noah Kim", "STU-10239", "Graduate", 0.19, "Routine academic monitoring", [
    "Consistent grades across terms",
    "Moderate study time (6 hrs/week)",
    "No financial holds",
  ]),
  student("s10", "Fatima Rahman", "STU-10240", "Dropout", 0.88, "Financial aid outreach, Personal counseling", [
    "Tuition severely overdue (3 installments)",
    "Failed 4 of 5 courses",
    "26 absences this term",
  ]),
  student("s11", "Liam O'Connor", "STU-10241", "Enrolled", 0.58, "Academic support", [
    "Failed 2 of 6 courses",
    "Attendance rate 74%",
    "Study time below program average",
  ]),
  student("s12", "Grace Adeyemi", "STU-10242", "Graduate", 0.05, "Routine academic monitoring", [
    "Top-decile academic performance",
    "Tuition and scholarship in good standing",
    "Excellent attendance",
  ]),
];

export const RECENT_ACTIVITY_IDS = ["s10", "s1", "s4", "s7", "s3"];
export const RECENT_ACTIVITY_TIME_LABELS = [
  "6 minutes ago",
  "24 minutes ago",
  "1 hour ago",
  "2 hours ago",
  "Yesterday, 4:12 PM",
];
