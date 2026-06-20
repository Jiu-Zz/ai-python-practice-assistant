import { useEffect, useState } from "react";
import { ApiError, clearToken, getCurrentUser, hasStoredSession, login, register } from "./api/client";
import { AppShell } from "./components/AppShell";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LearningPathPage } from "./pages/LearningPathPage";
import { PracticePage } from "./pages/PracticePage";
import { ProblemBankPage } from "./pages/ProblemBankPage";
import { ProfilePage } from "./pages/ProfilePage";
import type { PageKey, User } from "./types";

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("dashboard");
  const [activeProblemId, setActiveProblemId] = useState(1);
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    async function restoreSession() {
      if (!hasStoredSession()) {
        setAuthReady(true);
        return;
      }
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        clearToken();
        setUser(null);
      } finally {
        setAuthReady(true);
      }
    }

    restoreSession();
  }, []);

  function openPractice(problemId: number) {
    setActiveProblemId(problemId);
    setCurrentPage("practice");
  }

  async function handleLogin(account: string, password: string) {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const nextUser = await login(account, password);
      setUser(nextUser);
      setCurrentPage("dashboard");
    } catch (error) {
      console.error("login failed", error);
      if (error instanceof ApiError) {
        setAuthError(error.message);
      } else if (error instanceof Error) {
        setAuthError(`${error.name}: ${error.message}`);
      } else {
        setAuthError(String(error));
      }
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleRegister(payload: {
    username: string;
    email: string;
    password: string;
    learning_stage: string;
    nickname?: string;
  }) {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const nextUser = await register(payload);
      setUser(nextUser);
      setCurrentPage("dashboard");
    } catch (error) {
      console.error("register failed", error);
      if (error instanceof ApiError) {
        setAuthError(error.message);
      } else if (error instanceof Error) {
        setAuthError(`${error.name}: ${error.message}`);
      } else {
        setAuthError(String(error));
      }
    } finally {
      setAuthLoading(false);
    }
  }

  function handleLogout() {
    clearToken();
    setUser(null);
    setAuthError(null);
  }

  if (!authReady) {
    return <div className="loading-screen">正在恢复会话...</div>;
  }

  if (!user) {
    return (
      <AuthPage
        onLogin={handleLogin}
        onRegister={handleRegister}
        loading={authLoading}
        error={authError}
      />
    );
  }

  return (
    <AppShell currentPage={currentPage} onPageChange={setCurrentPage} user={user} onLogout={handleLogout}>
      {currentPage === "dashboard" && <DashboardPage user={user} onPractice={openPractice} />}
      {currentPage === "problems" && <ProblemBankPage onPractice={openPractice} />}
      {currentPage === "practice" && <PracticePage problemId={activeProblemId} />}
      {currentPage === "path" && <LearningPathPage onPractice={openPractice} />}
      {currentPage === "profile" && <ProfilePage user={user} onPractice={openPractice} />}
    </AppShell>
  );
}
