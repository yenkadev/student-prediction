import { useEffect, useState } from "react";
import { apiClient } from "./api/client";
import type { ConversationDetail } from "./api/types";
import { AllSessions } from "./components/AllSessions";
import { AllStudents } from "./components/AllStudents";
import { BatchResults } from "./components/BatchResults";
import { ContinueChat } from "./components/ContinueChat";
import { Dashboard } from "./components/Dashboard";
import { Header } from "./components/Header";
import { NewAssessment } from "./components/NewAssessment";
import { Sidebar } from "./components/Sidebar";
import { StudentDetail } from "./components/StudentDetail";
import type { RiskLevel, Student } from "./types";
import "./App.css";

export type View = "dashboard" | "new" | "batch" | "student" | "continue" | "sessions" | "students";
type InputMode = "chat" | "form" | "upload";
const BATCH_STORAGE_KEY = "student-risk-batch-results";

function loadSavedBatch(): Student[] {
  try {
    const value = window.localStorage.getItem(BATCH_STORAGE_KEY);
    return value ? (JSON.parse(value) as Student[]) : [];
  } catch {
    return [];
  }
}

const PAGE_COPY: Record<View, { title: string; subtitle: string }> = {
  dashboard: { title: "Overview", subtitle: "Snapshot of assessed students and quick actions" },
  new: { title: "New assessment", subtitle: "Describe a student or upload a batch file for assessment" },
  batch: { title: "Batch results", subtitle: "Review predicted risk across the uploaded batch" },
  student: { title: "Student detail", subtitle: "Full risk profile and academic data" },
  continue: { title: "Continue assessment", subtitle: "Resume a previous chat conversation" },
  sessions: { title: "All sessions", subtitle: "Every chat and batch assessment" },
  students: { title: "All students", subtitle: "Every individually assessed student" },
};

function App() {
  const [view, setView] = useState<View>("dashboard");
  const [newAssessmentMode, setNewAssessmentMode] = useState<InputMode>("chat");
  const [batchData, setBatchData] = useState<Student[]>(loadSavedBatch);
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
  const [prevView, setPrevView] = useState<View>("dashboard");
  const [resumeConversation, setResumeConversation] = useState<ConversationDetail | null>(null);
  const [studentsFilter, setStudentsFilter] = useState<RiskLevel | undefined>(undefined);

  useEffect(() => {
    try {
      window.localStorage.setItem(BATCH_STORAGE_KEY, JSON.stringify(batchData));
    } catch {
      // Nếu trình duyệt hết dung lượng, kết quả vẫn được giữ trong phiên hiện tại.
    }
  }, [batchData]);

  function goToNewChat() {
    setResumeConversation(null);
    setNewAssessmentMode("chat");
    setView("new");
  }

  function goToUpload() {
    setResumeConversation(null);
    setNewAssessmentMode("upload");
    setView("new");
  }

  function goToBatchFromOverview(jobId: string) {
    apiClient.getBatchJob(jobId).then((job) => {
      if (job.results) {
        setBatchData(job.results);
        setView("batch");
      }
    });
  }

  function continueChat(conversationId: string) {
    apiClient.getConversation(conversationId).then((conv) => {
      setPrevView(view);
      setResumeConversation(conv);
      setView("continue");
    });
  }

  function goToStudent(id: string) {
    setPrevView(view);
    setSelectedStudentId(id);
    setView("student");
  }

  const selectedBatchStudent = selectedStudentId
    ? batchData.find((student) => student.id === selectedStudentId)
    : undefined;

  function goBack() {
    setView(prevView);
  }

  function handleToggleReviewed(id: string) {
    setBatchData((prev) => prev.map((s) => (s.id === id ? { ...s, reviewed: !s.reviewed } : s)));
  }

  const { title, subtitle } = PAGE_COPY[view];

  return (
    <div className="app-shell">
      <Sidebar view={view} onNavigate={setView} />
      <div className="app-shell__content">
        <Header title={title} subtitle={subtitle} />
        <main className="app-shell__scroll">
          {view === "dashboard" && (
            <Dashboard
              onStartChat={goToNewChat}
              onStartUpload={goToUpload}
              onSelectStudent={goToStudent}
              onViewBatch={goToBatchFromOverview}
              onContinueChat={continueChat}
              onViewAllSessions={() => setView("sessions")}
              onViewAllStudents={(filter) => { setStudentsFilter(filter); setView("students"); }}
            />
          )}
          {view === "sessions" && (
            <AllSessions
              onSelectStudent={goToStudent}
              onViewBatch={goToBatchFromOverview}
              onContinueChat={continueChat}
            />
          )}
          {view === "students" && (
            <AllStudents onSelectStudent={goToStudent} filterRisk={studentsFilter} />
          )}
          {view === "new" && (
            <NewAssessment
              key={newAssessmentMode}
              initialMode={newAssessmentMode}
              onBatchComplete={(students) => {
                setBatchData(students);
                setView("batch");
              }}
            />
          )}
          {view === "continue" && resumeConversation && (
            <ContinueChat conversation={resumeConversation} onBack={goBack} />
          )}
          {view === "batch" && (
            <BatchResults
              students={batchData}
              onGoToUpload={goToUpload}
              onToggleReviewed={handleToggleReviewed}
              onSelectStudent={goToStudent}
            />
          )}
          {view === "student" && selectedStudentId && (
            <StudentDetail
              studentId={selectedStudentId}
              batchStudent={selectedBatchStudent}
              onBack={goBack}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
