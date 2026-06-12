from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


problem_knowledge_points = Table(
    "problem_knowledge_points",
    Base.metadata,
    Column("problem_id", ForeignKey("problems.id"), primary_key=True),
    Column("knowledge_point_id", ForeignKey("knowledge_points.id"), primary_key=True),
)


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(64), nullable=True)
    role = Column(String(32), nullable=False, default="student")
    learning_stage = Column(String(32), nullable=False, default="basic")

    run_records = relationship("RunRecord", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    ai_records = relationship("AiRecord", back_populates="user")
    recommendations = relationship("LearningRecommendation", back_populates="user")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    category = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)

    problems = relationship(
        "Problem",
        secondary=problem_knowledge_points,
        back_populates="knowledge_points",
    )
    recommendations = relationship("LearningRecommendation", back_populates="target_knowledge_point")


class Problem(Base, TimestampMixin):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(String(32), nullable=False, default="beginner")
    input_description = Column(Text, nullable=True)
    output_description = Column(Text, nullable=True)
    sample_input = Column(Text, nullable=True)
    sample_output = Column(Text, nullable=True)
    starter_code = Column(Text, nullable=True)
    reference_solution = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="published")
    pass_rate = Column(Integer, nullable=False, default=70)

    knowledge_points = relationship(
        "KnowledgePoint",
        secondary=problem_knowledge_points,
        back_populates="problems",
    )
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    run_records = relationship("RunRecord", back_populates="problem")
    submissions = relationship("Submission", back_populates="problem")
    ai_records = relationship("AiRecord", back_populates="problem")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_sample = Column(Boolean, nullable=False, default=False)
    weight = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    problem = relationship("Problem", back_populates="test_cases")
    test_results = relationship("TestResult", back_populates="test_case")


class RunRecord(Base):
    __tablename__ = "run_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    stdin = Column(Text, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    status = Column(String(32), nullable=False)
    error_type = Column(String(64), nullable=True)
    time_ms = Column(Integer, nullable=False, default=0)
    memory_kb = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="run_records")
    problem = relationship("Problem", back_populates="run_records")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    passed_count = Column(Integer, nullable=False, default=0)
    total_count = Column(Integer, nullable=False, default=0)
    error_type = Column(String(64), nullable=True)
    score = Column(Integer, nullable=False, default=0)
    time_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    test_results = relationship("TestResult", back_populates="submission", cascade="all, delete-orphan")
    ai_records = relationship("AiRecord", back_populates="submission")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    actual_output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    time_ms = Column(Integer, nullable=False, default=0)

    submission = relationship("Submission", back_populates="test_results")
    test_case = relationship("TestCase", back_populates="test_results")


class AiRecord(Base):
    __tablename__ = "ai_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True, index=True)
    request_type = Column(String(32), nullable=False)
    prompt_summary = Column(Text, nullable=True)
    response_json = Column(Text, nullable=False)
    hint_level = Column(Integer, nullable=True)
    confidence = Column(String(32), nullable=False, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="ai_records")
    problem = relationship("Problem", back_populates="ai_records")
    submission = relationship("Submission", back_populates="ai_records")


class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    reason = Column(Text, nullable=False)
    recommended_problem_ids = Column(Text, nullable=False, default="[]")
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="recommendations")
    target_knowledge_point = relationship("KnowledgePoint", back_populates="recommendations")
