import { useEffect, useState } from "react";
import { AppShell } from "./components/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { LearningPathPage } from "./pages/LearningPathPage";
import { PracticePage } from "./pages/PracticePage";
import { ProblemBankPage } from "./pages/ProblemBankPage";
import { ProfilePage } from "./pages/ProfilePage";
import { loginDemo } from "./api/client";
import type { PageKey, User } from "./types";

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("dashboard");
  const [activeProblemId, setActiveProblemId] = useState(2);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    loginDemo().then(setUser);
  }, []);

  function openPractice(problemId: number) {
    setActiveProblemId(problemId);
    setCurrentPage("practice");
  }

  return (
    <AppShell currentPage={currentPage} onPageChange={setCurrentPage} user={user}>
      {currentPage === "dashboard" && <DashboardPage onPractice={openPractice} />}
      {currentPage === "problems" && <ProblemBankPage onPractice={openPractice} />}
      {currentPage === "practice" && <PracticePage problemId={activeProblemId} />}
      {currentPage === "path" && <LearningPathPage onPractice={openPractice} />}
      {currentPage === "profile" && <ProfilePage user={user} onPractice={openPractice} />}
    </AppShell>
  );
}
