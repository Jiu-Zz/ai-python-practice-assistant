import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getProblems } from "../api/client";
import { ProblemTable } from "../components/ProblemTable";
import type { ProblemSummary } from "../types";

type ProblemBankPageProps = {
  onPractice: (problemId: number) => void;
};

export function ProblemBankPage({ onPractice }: ProblemBankPageProps) {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [keyword, setKeyword] = useState("");
  const [difficulty, setDifficulty] = useState("all");

  useEffect(() => {
    getProblems().then(setProblems);
  }, []);

  const filtered = useMemo(() => {
    return problems.filter((problem) => {
      const matchesKeyword =
        !keyword ||
        problem.title.includes(keyword) ||
        problem.knowledge_points.some((point) => point.includes(keyword));
      const matchesDifficulty = difficulty === "all" || problem.difficulty === difficulty;
      return matchesKeyword && matchesDifficulty;
    });
  }, [difficulty, keyword, problems]);

  return (
    <div className="page-stack">
      <section className="workspace-panel filter-row">
        <label className="search-box">
          <Search size={17} />
          <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索题目或知识点" />
        </label>
        <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
          <option value="all">全部难度</option>
          <option value="beginner">入门</option>
          <option value="basic">基础</option>
          <option value="intermediate">进阶</option>
        </select>
      </section>
      <ProblemTable problems={filtered} onPractice={onPractice} />
    </div>
  );
}
