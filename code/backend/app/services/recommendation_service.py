from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AiRecord, KnowledgePoint, Problem, Submission, User


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_today_recommendations(self, current_user: User) -> List[dict]:
        weak_points = self.analyze_weak_points(current_user)
        query = select(Problem).where(Problem.status == "published")
        if weak_points:
            query = query.join(Problem.knowledge_points).where(KnowledgePoint.name.in_(weak_points))
        problems = list(self.db.scalars(query.order_by(Problem.pass_rate.desc(), Problem.id.asc())).unique())[:5]
        return [self._problem_card(problem, weak_points) for problem in problems]

    def get_learning_path(self, current_user: User) -> dict:
        mastery = self._knowledge_mastery(current_user)
        topics = []
        for name, score in sorted(mastery.items(), key=lambda item: item[1])[:5]:
            if score < 0.4:
                status = "薄弱"
                reason = "最近提交通过率偏低，建议先补基础题。"
            elif score < 0.7:
                status = "巩固中"
                reason = "已经有一定掌握，可以继续做同难度练习。"
            else:
                status = "掌握较好"
                reason = "可以尝试更高难度或综合题。"
            topics.append({"name": name, "mastery": round(score, 2), "status": status, "reason": reason})

        recommendations = self.get_today_recommendations(current_user)
        return {
            "current_stage": current_user.learning_stage,
            "summary": "根据最近提交记录生成学习路径；记录较少时优先推荐基础知识点。",
            "recommended_topics": topics,
            "recommended_problem_ids": [item["id"] for item in recommendations],
        }

    def analyze_weak_points(self, current_user: User) -> List[str]:
        submissions = self._recent_submissions(current_user, limit=20)
        weak_counter = Counter()
        for submission in submissions:
            if submission.status == "accepted":
                continue
            for kp in submission.problem.knowledge_points:
                weak_counter[kp.name] += 1
        if weak_counter:
            return [name for name, _ in weak_counter.most_common(5)]
        return [kp.name for kp in self.db.scalars(select(KnowledgePoint).limit(3)).all()]

    def _knowledge_mastery(self, current_user: User) -> Dict[str, float]:
        points = self.db.scalars(select(KnowledgePoint).order_by(KnowledgePoint.id.asc())).all()
        mastery = {point.name: 0.5 for point in points}
        submissions = self._recent_submissions(current_user, limit=50)
        totals = defaultdict(int)
        accepted = defaultdict(int)
        for submission in submissions:
            for kp in submission.problem.knowledge_points:
                totals[kp.name] += 1
                if submission.status == "accepted":
                    accepted[kp.name] += 1
        for name, total in totals.items():
            mastery[name] = accepted[name] / total if total else 0.5
        return mastery

    def _recent_submissions(self, current_user: User, limit: int) -> List[Submission]:
        return self.db.scalars(
            select(Submission)
            .where(Submission.user_id == current_user.id)
            .order_by(Submission.created_at.desc())
            .limit(limit)
        ).all()

    @staticmethod
    def _problem_card(problem: Problem, weak_points: List[str]) -> dict:
        tags = [kp.name for kp in problem.knowledge_points]
        matched = [tag for tag in tags if tag in weak_points]
        return {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "pass_rate": problem.pass_rate,
            "knowledge_points": tags,
            "reason": f"针对薄弱点：{', '.join(matched)}" if matched else "适合当前阶段继续练习",
        }


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.recommendations = RecommendationService(db)

    def get_dashboard(self, current_user: User) -> dict:
        submissions = self.db.scalars(
            select(Submission)
            .where(Submission.user_id == current_user.id)
            .order_by(Submission.created_at.desc())
            .limit(50)
        ).all()
        ai_request_count = self.db.query(AiRecord).filter(AiRecord.user_id == current_user.id).count()
        completed_problem_ids = {item.problem_id for item in submissions}
        accepted_problem_ids = {item.problem_id for item in submissions if item.status == "accepted"}
        recent = submissions[:10]
        recent_pass_rate = (
            len([item for item in recent if item.status == "accepted"]) / len(recent)
            if recent
            else 0.0
        )
        errors = Counter(item.error_type for item in submissions if item.error_type)
        return {
            "completed_problem_count": len(completed_problem_ids),
            "accepted_problem_count": len(accepted_problem_ids),
            "recent_pass_rate": round(recent_pass_rate, 2),
            "top_error_types": [name for name, _ in errors.most_common(3)],
            "weak_knowledge_points": self.recommendations.analyze_weak_points(current_user),
            "trend": self._trend(submissions),
            "ai_request_count": ai_request_count,
        }

    @staticmethod
    def _trend(submissions: List[Submission]) -> List[dict]:
        by_day = defaultdict(list)
        for item in submissions:
            day = item.created_at.date().isoformat()
            by_day[day].append(item)
        trend = []
        for day in sorted(by_day.keys())[-7:]:
            items = by_day[day]
            rate = len([item for item in items if item.status == "accepted"]) / len(items)
            trend.append({"date": day, "pass_rate": round(rate, 2)})
        if not trend:
            today = datetime.utcnow().date().isoformat()
            trend.append({"date": today, "pass_rate": 0.0})
        return trend
