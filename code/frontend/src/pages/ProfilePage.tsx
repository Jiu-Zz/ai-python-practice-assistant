import { BookOpen, History, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { getDashboard, getRecommendations, getSubmissionHistory } from "../api/client";
import { StatTile } from "../components/StatTile";
import type { Dashboard, Recommendation, SubmissionHistoryItem, User } from "../types";

type ProfilePageProps = {
  user: User | null;
  onPractice: (problemId: number) => void;
};

export function ProfilePage({ user, onPractice }: ProfilePageProps) {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [history, setHistory] = useState<SubmissionHistoryItem[]>([]);

  useEffect(() => {
    getDashboard().then(setDashboard);
    getRecommendations().then(setRecommendations);
    getSubmissionHistory().then(setHistory);
  }, []);

  return (
    <div className="page-grid profile-grid">
      <section className="workspace-panel profile-head">
        <UserRound size={36} />
        <div>
          <h2>{user?.nickname ?? user?.username ?? "演示学生"}</h2>
          <p>{user?.email ?? "student@example.com"}</p>
        </div>
        <span className="difficulty-pill">{user?.learning_stage ?? "basic"}</span>
      </section>

      <div className="stat-grid">
        <StatTile label="累计做题" value={dashboard?.completed_problem_count ?? 0} tone="green" />
        <StatTile label="通过题目" value={dashboard?.accepted_problem_count ?? 0} tone="blue" />
        <StatTile label="AI 提示" value={dashboard?.ai_request_count ?? 0} tone="orange" />
      </div>

      <section className="workspace-panel">
        <div className="section-heading">
          <History size={18} />
          <h2>最近提交</h2>
        </div>
        <div className="history-list">
          {history.length > 0 ? (
            history.slice(0, 5).map((item) => (
              <article className="history-item" key={item.id}>
                <div>
                  <strong>{item.problem_title}</strong>
                  <span>{item.status} · {item.score} 分</span>
                </div>
                <button className="command-button" type="button" onClick={() => onPractice(item.problem_id)}>
                  <BookOpen size={16} />
                  继续练习
                </button>
              </article>
            ))
          ) : (
            <p className="muted">还没有提交记录，先去练一题吧。</p>
          )}
        </div>
      </section>
    </div>
  );
}
