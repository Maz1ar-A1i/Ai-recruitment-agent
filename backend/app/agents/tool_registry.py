"""Centralized Tool Registry for Agentic AI Orchestration."""
import logging
import inspect
from typing import Callable, Any, Optional
from pydantic import BaseModel
from app.schemas.agent import ToolInfo
from app.tools.job_analyzer import extract_job_requirements
from app.tools.resume_parser import parse_resume
from app.tools.skill_extractor import extract_candidate_skills
from app.tools.candidate_matcher import match_candidate_to_job
from app.tools.skill_gap_analyzer import identify_skill_gaps
from app.tools.score_calculator import calculate_candidate_score
from app.tools.interview_generator import generate_interview_questions
from app.tools.report_generator import generate_candidate_report
from app.tools.report_validator import validate_candidate_report
from app.tools.semantic_search import compute_semantic_similarity

logger = logging.getLogger(__name__)


class RegisteredTool:
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        input_schema: Optional[dict[str, Any]] = None,
        output_schema: Optional[dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.func = func
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    """Central registry storing available agent tools and metadata."""

    def __init__(self):
        self._tools: dict[str, RegisteredTool] = {}
        self._register_default_tools()

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        input_schema: Optional[dict[str, Any]] = None,
        output_schema: Optional[dict[str, Any]] = None
    ):
        self._tools[name] = RegisteredTool(
            name=name,
            description=description,
            func=func,
            input_schema=input_schema,
            output_schema=output_schema
        )
        logger.info("Registered agent tool: %s", name)

    def get_tool(self, name: str) -> Optional[RegisteredTool]:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolInfo]:
        return [
            ToolInfo(
                name=t.name,
                description=t.description,
                input_schema=t.input_schema,
                output_schema=t.output_schema
            )
            for t in self._tools.values()
        ]

    def execute_tool(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        return tool.execute(**kwargs)

    def _register_default_tools(self):
        self.register(
            name="extract_job_requirements",
            description="Analyzes job description to extract required/preferred skills, experience, and education.",
            func=extract_job_requirements,
            input_schema={"job_description": "str"},
            output_schema={"type": "JobRequirements"}
        )

        self.register(
            name="parse_resume",
            description="Parses resume text into structured candidate profile with sensitive info de-biasing.",
            func=parse_resume,
            input_schema={"resume_text": "str"},
            output_schema={"type": "CandidateProfile"}
        )

        self.register(
            name="extract_candidate_skills",
            description="Normalizes candidate skills using alias mapping (e.g. Postgres -> PostgreSQL).",
            func=extract_candidate_skills,
            input_schema={"candidate_profile": "CandidateProfile", "raw_text": "Optional[str]"},
            output_schema={"type": "list[str]"}
        )

        self.register(
            name="match_candidate_to_job",
            description="Compares candidate profile with job requirements and extracts verbatim evidence citations.",
            func=match_candidate_to_job,
            input_schema={"job_requirements": "JobRequirements", "candidate_profile": "CandidateProfile"},
            output_schema={"type": "SkillMatchResult"}
        )

        self.register(
            name="identify_skill_gaps",
            description="Determines missing and partial skills, assigning Critical, Moderate, or Minor severity.",
            func=identify_skill_gaps,
            input_schema={"job_requirements": "JobRequirements", "match_result": "SkillMatchResult"},
            output_schema={"type": "SkillGapResult"}
        )

        self.register(
            name="calculate_candidate_score",
            description="Computes transparent, deterministic mathematical score out of 100 with configurable weights.",
            func=calculate_candidate_score,
            input_schema={"job_requirements": "JobRequirements", "candidate_profile": "CandidateProfile", "match_result": "SkillMatchResult"},
            output_schema={"type": "ScoreBreakdown"}
        )

        self.register(
            name="generate_interview_questions",
            description="Generates personalized interview questions across Technical, Project, Gap, and Behavioral categories.",
            func=generate_interview_questions,
            input_schema={
                "job_requirements": "JobRequirements",
                "candidate_profile": "CandidateProfile",
                "match_result": "SkillMatchResult",
                "gap_result": "SkillGapResult"
            },
            output_schema={"type": "InterviewQuestionsResult"}
        )

        self.register(
            name="generate_candidate_report",
            description="Synthesizes structured evaluation dimensions into a comprehensive executive report.",
            func=generate_candidate_report,
            input_schema={
                "job_requirements": "JobRequirements",
                "candidate_profile": "CandidateProfile",
                "match_result": "SkillMatchResult",
                "gap_result": "SkillGapResult",
                "score_breakdown": "ScoreBreakdown",
                "interview_result": "InterviewQuestionsResult"
            },
            output_schema={"type": "CandidateReport"}
        )

        self.register(
            name="validate_candidate_report",
            description="Enforces report integrity, score mathematical consistency, and evidence backing.",
            func=validate_candidate_report,
            input_schema={
                "report": "CandidateReport",
                "job_requirements": "JobRequirements",
                "candidate_profile": "CandidateProfile"
            },
            output_schema={"type": "ValidationResult"}
        )

        self.register(
            name="compute_semantic_similarity",
            description="Calculates TF-IDF and cosine similarity between role description and candidate experiences.",
            func=compute_semantic_similarity,
            input_schema={"job_text": "str", "candidate_experience_texts": "list[str]"},
            output_schema={"type": "dict"}
        )


# Global registry instance
tool_registry = ToolRegistry()
