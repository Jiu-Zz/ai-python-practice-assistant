import { BookOpen, History, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { getDashboard, getRecommendations } from "../api/client";
import { StatTile } from "../components/StatTile";
import type { Dashboard, Recommendation, User } from "../types";

type ProfilePageProps = {
  user: User | null;
  onPractice: (problemId: number) => void;
};

export function ProfilePage({ user, onPractice }: ProfilePageProps) {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    getDashboard().then(setDashboard);
    getRecommendations().then(setRecommendations);
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
        <StatTile label="AI 提示" value={23} tone="orange" />
      </div>

      <section className="workspace-panel">
        <div className="section-heading">
          <History size={18} />
          <h2>错题本</h2>
        </div>
        <div className="problem-list">
          {recommendations.slice(0, 3).map((item) => (
            <article className="problem-card" key={item.id}>
              <div>
                <strong>{item.title}</strong>
                <span>{item.reason}</span>
              </div>
              <button className="command-button" type="button" onClick={() => onPractice(item.id)}>
                <BookOpen size={16} />
                练习
              </button>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
