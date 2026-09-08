"""Typed state representation for Recruitment Agent."""
from typing import Optional, Any
from pydantic import BaseModel, Field
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import (
    SkillMatchResult,
    SkillGapResult,
    ScoreBreakdown,
    InterviewQuestionsResult,
    CandidateReport,
    ValidationResult,
)


class RecruitmentState(BaseModel):
    """Strongly typed state container for recruitment agent execution."""
    run_id: str
    task: str = "Evaluate candidate against job requirements"
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None

    # Input data
    job_description: Optional[str] = None
    raw_resume_text: Optional[str] = None
    sanitized_resume_text: Optional[str] = None

    # Intermediate tool outputs
    job_requirements: Optional[JobRequirements] = None
    candidate_profile: Optional[CandidateProfile] = None
    candidate_skills: list[str] = Field(default_factory=list)
    skill_match: Optional[SkillMatchResult] = None
    skill_gaps: Optional[SkillGapResult] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    interview_result: Optional[InterviewQuestionsResult] = None
    candidate_report: Optional[CandidateReport] = None
    validation_result: Optional[ValidationResult] = None

    # Execution tracking
    step_history: list[dict[str, Any]] = Field(default_factory=list)
    current_step: int = 0
    is_completed: bool = False
    error: Optional[str] = None
