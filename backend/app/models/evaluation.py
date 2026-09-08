"""Evaluation and Interview Question SQLAlchemy Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    agent_run_id = Column(String(36), nullable=True)

    overall_score = Column(Float, nullable=False, default=0.0)
    recommendation = Column(String(50), nullable=False, default="Potential Match")
    skill_match_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    preferred_skills_score = Column(Float, default=0.0)
    projects_score = Column(Float, default=0.0)

    matching_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    partial_matches = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    potential_concerns = Column(JSON, default=list)
    evidence_snippets = Column(JSON, default=list)
    ai_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="evaluations")
    candidate = relationship("Candidate", back_populates="evaluations")
    interview_questions = relationship("InterviewQuestion", back_populates="evaluation", cascade="all, delete-orphan")
    decisions = relationship("RecruiterDecision", back_populates="evaluation", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id = Column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # Technical, Project-based, Experience-based, Skill-gap, Behavioral
    question = Column(Text, nullable=False)
    target_skill_or_gap = Column(String(255), nullable=True)
    rationale = Column(Text, nullable=True)
    suggested_answer_points = Column(JSON, default=list)

    evaluation = relationship("Evaluation", back_populates="interview_questions")
