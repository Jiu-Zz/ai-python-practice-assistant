import { ArrowRight, Route } from "lucide-react";
import { useEffect, useState } from "react";
import { getLearningPath } from "../api/client";
import type { LearningPath } from "../types";

type LearningPathPageProps = {
  onPractice: (problemId: number) => void;
};

export function LearningPathPage({ onPractice }: LearningPathPageProps) {
  const [path, setPath] = useState<LearningPath | null>(null);

  useEffect(() => {
    getLearningPath().then(setPath);
  }, []);

  return (
    <div className="page-stack">
      <section className="workspace-panel intro-panel">
        <div>
          <p className="eyebrow">当前阶段</p>
          <h2>{path?.current_stage ?? "basic"}</h2>
          <p>{path?.summary}</p>
        </div>
        <button
          className="primary-button"
          type="button"
          onClick={() => onPractice(path?.recommended_problem_ids[0] ?? 2)}
        >
          <ArrowRight size={17} />
          下一题
        </button>
      </section>

      <section className="path-list">
        {path?.recommended_topics.map((topic, index) => (
          <article className="path-item" key={topic.name}>
            <div className="path-index">{index + 1}</div>
            <div>
              <div className="section-heading compact">
                <Route size={17} />
                <h2>{topic.name}</h2>
              </div>
              <p>{topic.reason}</p>
              <div className="progress-track">
                <span style={{ width: `${topic.mastery * 100}%` }} />
              </div>
            </div>
            <strong>{topic.status}</strong>
          </article>
        ))}
      </section>
    </div>
  );
}
