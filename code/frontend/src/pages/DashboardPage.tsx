import { ArrowRight, BookOpenCheck, Flame, Target, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { getDashboard, getRecommendations } from "../api/client";
import { StatTile } from "../components/StatTile";
import type { Dashboard, Recommendation } from "../types";
import { difficultyLabel } from "../utils/format";

type DashboardPageProps = {
  onPractice: (problemId: number) => void;
};

export function DashboardPage({ onPractice }: DashboardPageProps) {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    getDashboard().then(setDashboard);
    getRecommendations().then(setRecommendations);
  }, []);

  return (
    <div className="page-grid dashboard-grid">
      <section className="workspace-panel intro-panel">
        <div>
          <p className="eyebrow">今日目标</p>
          <h2>完成 2 道基础题，重点巩固循环和列表</h2>
        </div>
        <button className="primary-button" type="button" onClick={() => onPractice(recommendations[0]?.id ?? 2)}>
          <Target size={17} />
          开始练习
        </button>
      </section>

      <div className="stat-grid">
        <StatTile label="累计做题" value={dashboard?.completed_problem_count ?? 0} tone="green" />
        <StatTile label="已通过" value={dashboard?.accepted_problem_count ?? 0} tone="blue" />
        <StatTile label="最近通过率" value={`${Math.round((dashboard?.recent_pass_rate ?? 0) * 100)}%`} tone="orange" />
      </div>

      <section className="workspace-panel">
        <div className="section-heading">
          <BookOpenCheck size={18} />
          <h2>今日推荐</h2>
        </div>
        <div className="problem-list">
          {recommendations.map((item) => (
            <article className="problem-card" key={item.id}>
              <div>
                <strong>{item.title}</strong>
                <span>{difficultyLabel(item.difficulty)} · 通过率 {item.pass_rate}%</span>
              </div>
              <p>{item.reason}</p>
              <div className="card-actions">
                <div className="tag-row">
                  {item.knowledge_points.map((point) => (
                    <span className="tag" key={point}>
                      {point}
                    </span>
                  ))}
                </div>
                <button className="icon-button" type="button" title="进入题目" onClick={() => onPractice(item.id)}>
                  <ArrowRight size={17} />
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="workspace-panel">
        <div className="section-heading">
          <TrendingUp size={18} />
          <h2>薄弱点</h2>
        </div>
        <div className="focus-list">
          {(dashboard?.weak_knowledge_points ?? []).map((point) => (
            <button className="focus-chip" key={point} type="button">
              <Flame size={15} />
              {point}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
