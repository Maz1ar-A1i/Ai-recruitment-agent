"""Mock LLM Provider for offline testing and deterministic demonstration."""
import re
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile, CandidateEducation, CandidateExperienceItem, CandidateProject
from app.schemas.evaluation import (
    SkillMatchResult,
    EvidenceSnippet,
    SkillGapResult,
    SkillGapItem,
    InterviewQuestionsResult,
    InterviewQuestionItem,
    CandidateReport,
    ScoreBreakdown,
    ValidationResult,
)

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM that generates valid Pydantic structures for all tools."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return "Mock LLM Response: Workflow executed successfully with verified evidence and transparent scoring."

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        model_name = response_model.__name__

        if model_name == "JobRequirements":
            return self._mock_job_requirements(prompt)
        elif model_name == "CandidateProfile":
            return self._mock_candidate_profile(prompt)
        elif model_name == "SkillMatchResult":
            return self._mock_skill_match(prompt)
        elif model_name == "SkillGapResult":
            return self._mock_skill_gaps(prompt)
        elif model_name == "InterviewQuestionsResult":
            return self._mock_interview_questions(prompt)
        elif model_name == "ValidationResult":
            return ValidationResult(
                is_valid=True,
                issues=[],
                repaired=False,
                details={
                    "score_consistency": True,
                    "evidence_alignment": True,
                    "recommendation_alignment": True
                }
            )

        # Fallback dynamic creation for other models
        try:
            return response_model()
        except Exception:
            raise ValueError(f"MockLLM cannot construct default for {model_name}")

    def _mock_job_requirements(self, prompt: str) -> JobRequirements:
        lower = prompt.lower()
        title = "Software Engineer"
        if "backend" in lower or "python" in lower:
            title = "Python Backend Engineer"
        elif "ai" in lower or "machine learning" in lower:
            title = "AI / ML Engineer"
        elif "data" in lower:
            title = "Data Engineer"
        elif "full" in lower or "react" in lower:
            title = "Full Stack Engineer"

        req_skills = ["Python", "FastAPI", "SQL", "REST APIs", "Git"]
        pref_skills = ["Docker", "AWS", "PostgreSQL", "Redis"]
        exp = 2.0
        if "senior" in lower:
            exp = 5.0
        elif "junior" in lower or "entry" in lower:
            exp = 1.0

        return JobRequirements(
            job_title=title,
            required_skills=req_skills,
            preferred_skills=pref_skills,
            experience_required=exp,
            education="Bachelor's degree in Computer Science or related field",
            responsibilities=[
                "Design and develop scalable RESTful APIs",
                "Maintain robust database schemas and queries",
                "Collaborate with frontend engineers and product managers",
                "Ensure test coverage and automated deployment pipelines"
            ],
            technical_requirements=[
                "Python 3.10+",
                "Relational databases (PostgreSQL/MySQL)",
                "Asynchronous programming (asyncio/FastAPI)",
                "Git version control and CI/CD"
            ],
            soft_skills=["Clear technical communication", "Problem solving", "Team collaboration"],
            keywords=["Backend", "Microservices", "REST", "Cloud", "API"]
        )

    def _mock_candidate_profile(self, prompt: str) -> CandidateProfile:
        name_match = re.search(r"(?:Name|Candidate):\s*([A-Za-z\s]+)", prompt, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "Alex Mercer"

        # Extract years of experience
        exp_years = 2.0
        exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs)", prompt, re.IGNORECASE)
        if exp_match:
            exp_years = float(exp_match.group(1))
        elif "6 months" in prompt.lower():
            exp_years = 0.5

        # Check for skills listed after SKILLS:
        skills_section_match = re.search(r"SKILLS:\s*([^\n\r]+)", prompt, re.IGNORECASE)
        if skills_section_match:
            raw_skills = [s.strip() for s in skills_section_match.group(1).split(",") if s.strip()]
            found_skills = raw_skills
        else:
            known = ["Python", "FastAPI", "Flask", "Django", "SQL", "PostgreSQL", "Docker", "AWS", "Git", "React", "TypeScript", "Redis", "PHP", "MySQL", "Java", "PyTorch", "Scikit-Learn"]
            found_skills = [s for s in known if re.search(rf"\b{re.escape(s)}\b", prompt, re.IGNORECASE)]
            if not found_skills:
                found_skills = ["Python", "FastAPI", "SQL", "Git"]

        return CandidateProfile(
            name=name,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            phone="+1 (555) 234-5678",
            summary="Engineering professional with proven technical background.",
            education=[
                CandidateEducation(
                    degree="B.S. in Computer Science" if "computer" in prompt.lower() or "data" in prompt.lower() else "Associate Degree",
                    institution="State University",
                    year="2022",
                    field_of_study="STEM"
                )
            ],
            experience=[
                CandidateExperienceItem(
                    role="Software Developer",
                    company="TechCorp Solutions",
                    duration="2022 - Present",
                    years=exp_years,
                    description=prompt[:300],
                    skills_used=found_skills[:4]
                )
            ],
            skills=found_skills,
            projects=[
                CandidateProject(
                    name="Core Service Implementation",
                    description="Hands-on software application project.",
                    technologies=found_skills[:3],
                    link="https://github.com/example/project"
                )
            ],
            certifications=[],
            years_of_experience=exp_years
        )

    def _mock_skill_match(self, prompt: str) -> SkillMatchResult:
        return SkillMatchResult(
            matching_skills=["Python", "FastAPI", "SQL", "REST APIs", "Git"],
            missing_skills=["AWS"],
            partial_matches=["Docker"],
            experience_match=True,
            education_match=True,
            overall_compatibility="High",
            evidence_snippets=[
                EvidenceSnippet(
                    skill="Python",
                    status="Strong Match",
                    snippet="Engineered high-throughput REST APIs using Python and FastAPI.",
                    source_section="Experience"
                ),
                EvidenceSnippet(
                    skill="FastAPI",
                    status="Strong Match",
                    snippet="Built an asynchronous RESTful inventory service with FastAPI, Redis caching, and PostgreSQL.",
                    source_section="Projects"
                ),
                EvidenceSnippet(
                    skill="SQL",
                    status="Match",
                    snippet="Optimized PostgreSQL database queries improving response times by 35%.",
                    source_section="Experience"
                ),
                EvidenceSnippet(
                    skill="Git",
                    status="Match",
                    snippet="Utilized Git for distributed version control across cross-functional team.",
                    source_section="Experience"
                ),
                EvidenceSnippet(
                    skill="Docker",
                    status="Partial",
                    snippet="Containerized local services during development using Docker compose.",
                    source_section="Projects"
                )
            ]
        )

    def _mock_skill_gaps(self, prompt: str) -> SkillGapResult:
        return SkillGapResult(
            gaps=[
                SkillGapItem(
                    skill="AWS",
                    severity="Minor",
                    rationale="Cloud deployment experience on AWS is preferred; candidate has strong container foundations and can onboard rapidly."
                ),
                SkillGapItem(
                    skill="Docker",
                    severity="Moderate",
                    rationale="Candidate demonstrated basic container usage, but lacks production Kubernetes cluster orchestration experience."
                )
            ]
        )

    def _mock_interview_questions(self, prompt: str) -> InterviewQuestionsResult:
        return InterviewQuestionsResult(
            questions=[
                InterviewQuestionItem(
                    category="Technical",
                    question="In your FastAPI service, how did you structure dependency injection and asynchronous database sessions?",
                    target_skill_or_gap="FastAPI",
                    rationale="Validates claimed architectural proficiency with FastAPI and async Python.",
                    suggested_answer_points=[
                        "Mentions Depends() and async session context managers",
                        "Discusses handling connection pools and lifecycle events"
                    ]
                ),
                InterviewQuestionItem(
                    category="Project-based",
                    question="Can you walk through the caching strategy implemented with Redis in your Inventory Management project?",
                    target_skill_or_gap="Redis",
                    rationale="Evaluates practical distributed caching decisions and cache invalidation policies.",
                    suggested_answer_points=[
                        "Explains cache-aside or write-through pattern",
                        "Addresses TTL and stale data handling"
                    ]
                ),
                InterviewQuestionItem(
                    category="Skill-gap",
                    question="What experience do you have deploying and monitoring containerized applications in cloud environments?",
                    target_skill_or_gap="AWS / Docker",
                    rationale="Assesses adaptability in missing cloud deployment areas.",
                    suggested_answer_points=[
                        "Shows willingness to learn ECS, EKS, or CloudWatch",
                        "Discusses basic Dockerfile multi-stage builds"
                    ]
                ),
                InterviewQuestionItem(
                    category="Behavioral",
                    question="Describe a time when you received feedback on an API design that required significant architectural rework.",
                    target_skill_or_gap="Collaboration",
                    rationale="Tests receptive attitude toward code review and iterative design.",
                    suggested_answer_points=[
                        "Demonstrates open-mindedness and focus on API consumers",
                        "Shows constructive resolution of technical disagreement"
                    ]
                )
            ]
        )
