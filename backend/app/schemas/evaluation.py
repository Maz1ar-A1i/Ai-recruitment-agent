"""Pydantic schemas for Evaluation, Matching, Scoring, and Reporting."""
from datetime import datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, ConfigDict


class EvidenceSnippet(BaseModel):
    skill: str
    status: str  # Strong Match, Match, Partial, Missing
    snippet: str
    source_section: Optional[str] = None


class SkillMatchResult(BaseModel):
    """Output of match_candidate_to_job tool."""
    matching_skills: list[str] = Field(default_factory=list, description="Directly matched required and preferred skills")
    missing_skills: list[str] = Field(default_factory=list, description="Required skills not found in candidate profile")
    partial_matches: list[str] = Field(default_factory=list, description="Related or adjacent skills identified")
    experience_match: bool = Field(True, description="Whether candidate meets experience threshold")
    education_match: bool = Field(True, description="Whether candidate meets education requirements")
    overall_compatibility: str = Field("Moderate", description="High, Moderate, Low")
    evidence_snippets: list[EvidenceSnippet] = Field(default_factory=list, description="Verbatim resume evidence for skills")


class SkillGapItem(BaseModel):
    skill: str
    severity: Literal["Critical", "Moderate", "Minor"] = Field("Moderate", description="Critical if required core skill, Minor if preferred")
    rationale: str = Field(..., description="Why this gap matters for the role")


class SkillGapResult(BaseModel):
    """Output of identify_skill_gaps tool."""
    gaps: list[SkillGapItem] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Deterministic score components calculated by score_calculator tool."""
    skills_score: float = Field(..., description="Calculated score for core required skills (0 to 50)")
    experience_score: float = Field(..., description="Calculated score for experience years/relevance (0 to 20)")
    education_score: float = Field(..., description="Calculated score for education degree/alignment (0 to 10)")
    preferred_skills_score: float = Field(..., description="Calculated score for nice-to-have skills (0 to 10)")
    projects_score: float = Field(..., description="Calculated score for relevant project experience (0 to 10)")
    overall_score: float = Field(..., description="Total weighted score out of 100")
    recommendation: Literal["Strong Match", "Match", "Potential Match", "Weak Match"]
    weights_applied: dict[str, float] = Field(default_factory=dict)


class InterviewQuestionItem(BaseModel):
    category: Literal["Technical", "Project-based", "Experience-based", "Skill-gap", "Behavioral"]
    question: str
    target_skill_or_gap: Optional[str] = None
    rationale: str
    suggested_answer_points: list[str] = Field(default_factory=list)


class InterviewQuestionsResult(BaseModel):
    """Output of generate_interview_questions tool."""
    questions: list[InterviewQuestionItem] = Field(default_factory=list)


class CandidateReport(BaseModel):
    """Structured report produced by generate_candidate_report tool."""
    candidate_name: str
    job_title: str
    overall_score: float
    recommendation: Literal["Strong Match", "Match", "Potential Match", "Weak Match"]
    score_breakdown: ScoreBreakdown
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    partial_matches: list[str] = Field(default_factory=list)
    experience_analysis: str = Field(..., description="Evaluation of experience depth and relevance")
    education_analysis: str = Field(..., description="Evaluation of academic qualifications")
    relevant_projects: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    skill_gaps: list[SkillGapItem] = Field(default_factory=list)
    potential_concerns: list[str] = Field(default_factory=list)
    interview_questions: list[InterviewQuestionItem] = Field(default_factory=list)
    evidence_snippets: list[EvidenceSnippet] = Field(default_factory=list)
    ai_explanation: str = Field(..., description="Synthesized executive explanation for the final recommendation")


class ValidationResult(BaseModel):
    """Output of validate_candidate_report tool."""
    is_valid: bool
    issues: list[str] = Field(default_factory=list)
    repaired: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


# API Schemas
class EvaluateCandidateRequest(BaseModel):
    job_id: str
    candidate_id: str


class BatchEvaluateRequest(BaseModel):
    job_id: str
    candidate_ids: list[str]


class EvaluationResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    agent_run_id: Optional[str] = None
    overall_score: float
    recommendation: str
    skill_match_score: float
    experience_score: float
    education_score: float
    preferred_skills_score: float
    projects_score: float
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    partial_matches: list[str] = Field(default_factory=list)
    skill_gaps: list[Any] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    potential_concerns: list[str] = Field(default_factory=list)
    evidence_snippets: list[Any] = Field(default_factory=list)
    ai_explanation: Optional[str] = None
    created_at: datetime
    interview_questions: list[Any] = Field(default_factory=list)
    decisions: list[Any] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class BatchEvaluateItem(BaseModel):
    candidate_id: str
    candidate_name: str
    status: str  # "SUCCESS", "FAILED"
    evaluation_id: Optional[str] = None
    score: Optional[float] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


class BatchEvaluateResponse(BaseModel):
    job_id: str
    total: int
    successful: int
    failed: int
    results: list[BatchEvaluateItem] = Field(default_factory=list)
